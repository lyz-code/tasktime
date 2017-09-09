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

    def __init__(self, data_location='~/.task', taskrc_location='~/.taskrc'):
        self.backend = tasklib.TaskWarrior(
            data_location=os.path.expanduser(data_location),
            taskrc_location=os.path.expanduser(taskrc_location))
        self.backend._get_history()
        self.print_never_active_tasks = False
        self.printer = ReadablePrinter()

    def set_printer(self, printer):
        self.printer = printer

    def set_null(self):
        self.printer.print_never_active_tasks = True

    def set_tasks(self, **kwargs):
        self.tasks = self.backend.tasks.filter(**kwargs)

    def query_report(self, **kwargs):
        self.set_tasks(**kwargs)

        total_time = 0
        for task in self.tasks:
            if task['status'] == 'recurring' or \
               task['status'] == 'deleted':
                continue
            active_time = task.active_time(args.period)
            self.printer.print_task(
                task["description"], active_time)
            total_time += active_time
        self.printer.print_result(total_time)


def load_parser(argv):
    ''' Configure parser '''
    description = "Calculate the spent time for a project or task " + \
                  "from taskwarrior"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--data_location", type=str, nargs='?',
                        default="~/.task", metavar="path",
                        help='Location of taskwarrior data (~/.task)')
    parser.add_argument("--taskrc_location", type=str, nargs='?',
                        default="~/.taskrc", metavar="path",
                        help='Location of taskwarrior config (~/.taskrc)')
    parser.add_argument("-o", "--output", nargs='?', type=str, choices=['csv'],
                        help='Output in specified format')

    parser.add_argument("-n", "--null", action="store_true",
                        help='Print also tasks without time information')
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("-v", "--verbose", action="count")
    verbosity.add_argument("-q", "--quiet", action="store_true")

    subparser = parser.add_subparsers(dest='subcommand', help='subcommands')

    project_parser = subparser.add_parser('project')
    task_parser = subparser.add_parser('task')

    project_parser.add_argument("project", type=str, help='Project name')
    project_parser.add_argument("-p", "--period", type=str, default=None,
                                help='Taskwarrior compatible date string')
    project_parser.add_argument("-s", "--status", type=str, default=None,
                                choices=['pending', 'completed', 'waiting'],
                                help='Tasks status')

    task_parser.add_argument("taskid", type=str, help='Taskwarrior task id')
    task_parser.add_argument("-p", "--period", type=str, default=None,
                             help='Taskwarrior compatible date string')

    return parser.parse_args()


if __name__ == "__main__":
    args = load_parser(sys.argv)
    tt = TaskTime(args.data_location, args.taskrc_location)

    if args.output:
        if args.output == 'csv':
            tt.set_printer(CSVPrinter())

    if args.null:
        tt.set_null()

    if args.subcommand == 'project':
        if args.status:
            tt.query_report(project=args.project, status=args.status)
        else:
            tt.query_report(project=args.project)
    elif args.subcommand == 'task':
        tt.query_report(id=args.taskid)
    elif args.subcommand == 'completed':
        tt.query_report(end__after='now - {}'.format(args.period))
