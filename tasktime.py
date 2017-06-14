#!/usr/bin/env python3

# Copyright (c) 2012 Sven Hertle <sven.hertle@googlemail.com>

import re
import sys
import json
import datetime
import argparse
import subprocess


class Calculator:
    printer = None

    task_cmd = "task"

    print_null = False

    def __init__(self):
        self.printer = ReadablePrinter()

    def setPrinter(self, printer):
        self.printer = printer

    def setTaskCmd(self, task_cmd):
        self.task_cmd = task_cmd

    def setPrintNull(self, print_null):
        self.print_null = print_null

    def create_statistic(self, project):
        if self.printer is None:
            print("Printer is None")
            sys.exit(1)

        # Get data from taskwarrior
        try:
            json_tmp = subprocess.check_output([self.task_cmd,
                                                "export",
                                                "pro:" + project,
                                                "rc.json.array=on"
                                                ])
        except OSError as e:
            print(str(e))
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print("Export from taskwarrior fails: {}".format(
                str(e.output, encoding="utf8")))
            sys.exit(1)

        # Make valid JSON
        json_str = str(json_tmp, encoding="utf8")

        # Parse JSON
        tasks = json.loads(json_str)

        # Print data
        self.printer.print_header(project)
        time = self.handle_tasks(tasks)
        self.printer.print_result(time)

    def handle_tasks(self, tasks):
        seconds = 0
        for t in tasks:
            tmp_seconds = self.get_task_time(t)
            seconds += tmp_seconds

            if self.print_null or tmp_seconds != 0:
                self.printer.print_task(t["description"], tmp_seconds)

        return seconds

    def get_task_time(self, task):
        seconds = 0

        last_start = ""
        if "annotations" in task:
            annotations = task["annotations"]
            for a in annotations:
                if a["description"] == "Started task":
                    last_start = a["entry"]
                elif a["description"] == "Stopped task":
                    seconds += self.calc_time_delta(last_start, a["entry"])

        return seconds

    def calc_time_delta(self, start, stop):
        start_time = self.internal_to_datetime(start)
        stop_time = self.internal_to_datetime(stop)

        delta = stop_time - start_time

        return delta.total_seconds()

    def internal_to_datetime(self, string):
        match = re.search(
            "^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z$", string)

        if match is None:
            return None

        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))

        hour = int(match.group(4))
        minute = int(match.group(5))
        second = int(match.group(6))

        return datetime.datetime(year, month, day, hour, minute, second)


class Printer:
    def print_header(self, project):
        raise NotImplementedError()

    def print_task(self, description, seconds):
        raise NotImplementedError()

    def print_result(self, seconds):
        raise NotImplementedError()

    def seconds_to_readable(self, seconds):
        second = seconds % 60
        minute = (seconds // 60) % 60
        hour = (seconds // 3600)

        return "{}:{}:{}".format(
            self._number_to_2_digits(hour),
            self._number_to_2_digits(minute),
            self._number_to_2_digits(second))

    def _number_to_2_digits(self, n):
        return repr(round(n)).zfill(2)


class CSVPrinter(Printer):
    def _csv_encode(self, string):
        return string.replace("\"", "\"\"")

    def print_header(self, project):
        print("\"Project\",\"" + self._csv_encode(project) + "\"")
        print("\"\",\"\"")
        print("\"Description\",\"Duration (hours)\"")
        print("\"\",\"\"")

    def print_task(self, description, seconds):
        print("\"{}\",\"{}\"".format(
            self._csv_encode(description), self.seconds_to_readable(seconds)))

    def print_result(self, seconds):
        print("\"\",\"\"")
        print("\"Sum\",\"" + self.seconds_to_readable(seconds) + "\"")


class ReadablePrinter(Printer):
    def print_header(self, project):
        print("Project: " + project)
        print()

    def print_task(self, description, seconds):
        print(description)
        if seconds != 0:
            print("\tDuration: " + self.seconds_to_readable(seconds))

    def print_result(self, seconds):
        print()
        print("Sum: " + self.seconds_to_readable(seconds))


def load_parser(argv):
    ''' Configure parser '''
    # Argparse
    description = "Calculate the spent time for a project from taskwarrior"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("project", type=str, help='Project name')
    parser.add_argument("-c", "--csv", action="store_true",
                        help='Print output in CSV format')
    parser.add_argument("-n", "--null", action="store_true",
                        help='Print also tasks without time information')
    parser.add_argument("-tc", "--task_command", type=str, nargs='?',
                        metavar="cmd", help='Change task command')

    return parser.parse_args()


if __name__ == "__main__":
    args = load_parser(sys.argv)

    c = Calculator()

    if args.csv:
        c.setPrinter(CSVPrinter())
    if args.null:
        c.setPrintNull(True)
    if args.task_command:
        c.setTaskCmd(args.task_command)

    c.create_statistic(args.project)
