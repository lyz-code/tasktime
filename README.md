tasktime
========

*tasktime* reads information of a project from [taskwarrior](http://www.taskwarrior.org) and calculates, how much time was spent with this project.
*tasktime* can print CSV or readable output.

## Usage

```
usage: tasktime [-h] [--data_location [path]] [-o [{csv}]] [-n] [-v | -q]
                {project,task} ...

Calculate the spent time for a project or task from taskwarrior

positional arguments:
  {project,task}        subcommands

optional arguments:
  -h, --help            show this help message and exit
  --data_location [path]
                        Location of taskwarrior data (~/.task)
  -o [{csv}], --output [{csv}]
                        Output in specified format
  -n, --null            Print also tasks without time information
  -v, --verbose
  -q, --quiet
```

## Prepare taskwarrior

You have to update the `tasklib` python package to the version that has the
`get_history` method. And configure the `history.cache` variables

## Note time with taskwarrior

taskwarrior has the operations *start* and *stop*.
This information is used to calculate the spent time.
You have to start and stop the tasks you work on.

Example:

```
task 2 start

# Work on task 2...

task 2 stop
```

## Examples

### Default output

```bash
tasktime project cool-project
```

Output:

```
Do something cool
    Duration: 00:13:05
Do something really cool
    Duration: 02:18:35

Sum: 02:31:40
```

### Print also tasks without time

```bash
tasktime -n project cool-project
```

Output:

```

Do something cool
    Duration: 00:13:05
Do something boring
Do something really cool
    Duration: 02:18:35

Sum: 02:31:40
```

### CSV output

```bash
tasktime -o csv project cool-project
```

Output:

```
"Project","cool-project"
"",""
"Description","Duration (hours)"
"",""
"Do something cool","00:13:05"
"Do something really cool","02:18:35"
"",""
"Sum","02:31:40"
```

### Print task information

```bash
tasktime task 20
```
Output
```
Do something really cool
    Duration: 02:18:35

Sum: 02:18:35
```

Contact and copyright
---------------------

Sven Hertle <<sven.hertle@googlemail.com>>

tasktime is distributed under the MIT license. See [http://www.opensource.org/licenses/MIT](http://www.opensource.org/licenses/MIT) for more information.
