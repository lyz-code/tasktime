#!/usr/bin/env python3

import os
import sys
import tasklib
import argparse


class Printer:
    def __init__(self, print_never_active_tasks=False):
        self.print_never_active_tasks = print_never_active_tasks

    def print_header(self, project):
        raise NotImplementedError()

    def print_task(self, description, seconds):
        raise NotImplementedError()

    def print_result(self, seconds):
        raise NotImplementedError()

    def seconds_to_readable(self, seconds):
        second = seconds % 60
        minute = (seconds // 60) % 60
        hour = (seconds // 3600) % 24
        days = (seconds // 86400)

        return "{}:{}:{}:{}".format(
            self._number_to_2_digits(days),
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
        if seconds != 0 or self.print_never_active_tasks:
            print(description)
        if seconds != 0:
            print("\tDuration: " + self.seconds_to_readable(seconds))

    def print_result(self, seconds):
        print()
        print("Sum: " + self.seconds_to_readable(seconds))


class TaskTime(object):

    def __init__(self, data_location='~/.task'):
        self.backend = tasklib.TaskWarrior(
            data_location=os.path.expanduser(data_location))
        self.backend._get_history()
        self.printer = ReadablePrinter()

    def set_printer(self, printer):
        self.printer = printer

    def set_null(self):
        self.printer.print_never_active_tasks = True

    def set_project(self, project):
        self.project = project

    def _set_tasks(self, filter):
        self.tasks = self.backend.tasks.filter(filter)

    def report(self, query):
        self._set_tasks(query)

        self.printer.print_header('Query: {}'.format(query))
        total_time = 0
        for task in self.tasks:
            if task['status'] == 'recurring':
                continue
            self.printer.print_task(
                task["description"], task.active_time())
            total_time += task.active_time
        self.printer.print_result(total_time)


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
    parser.add_argument("--task_command", type=str, nargs='?',
                        metavar="cmd", help='Change task command')
    parser.add_argument("--data_location", type=str, nargs='?',
                        default="~/.task", metavar="cmd",
                        help='Location of taskwarrior data')

    return parser.parse_args()


if __name__ == "__main__":
    args = load_parser(sys.argv)

    tt = TaskTime(args.data_location)
    if args.csv:
        tt.set_printer(CSVPrinter())
    if args.null:
        tt.set_null()
    tt.report("project={}".format(args.project))
