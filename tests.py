#!/usr/bin/env python3

import aurornis
import re

from os import environ
from typing import Union
from datetime import date

DEFAULT_ENVIRONMENT = {"PATH": environ["PATH"]}
KOSMORRO = ["./kosmorro", "--no-color"]


def execute(command, environment: {str: Union[int, str]} = None) -> aurornis.CommandResult:
    if environment is None:
        environment = DEFAULT_ENVIRONMENT
    else:
        for variable in DEFAULT_ENVIRONMENT:
            environment[variable] = DEFAULT_ENVIRONMENT[variable]

    return aurornis.run(command, environment)


def assert_nb_lines(expected_nb: int, in_str: str):
    """Check that the string has the specified number of lines and that the last one is empty."""
    lines = in_str.split("\n")
    assert len(lines) == expected_nb
    assert lines[len(lines) - 1] == ""


def test_help_message():
    result = execute(KOSMORRO + ['--help'])
    assert result.is_successful()
    assert result.stderr == ""
    assert result.stdout == """usage: kosmorro [-h] [--version] [--format {text,json,pdf}]
                [--latitude LATITUDE] [--longitude LONGITUDE] [--date DATE]
                [--timezone TIMEZONE] [--no-colors] [--output OUTPUT]
                [--no-graph] [--debug]

Compute the ephemerides and the events for a given date and a given position
on Earth.

optional arguments:
  -h, --help            show this help message and exit
  --version, -v         Show the program version
  --format {text,json,pdf}, -f {text,json,pdf}
                        The format to output the information to
  --latitude LATITUDE, -lat LATITUDE
                        The observer's latitude on Earth. Can also be set in
                        the KOSMORRO_LATITUDE environment variable.
  --longitude LONGITUDE, -lon LONGITUDE
                        The observer's longitude on Earth. Can also be set in
                        the KOSMORRO_LONGITUDE environment variable.
  --date DATE, -d DATE  The date for which the ephemerides must be calculated.
                        Can be in the YYYY-MM-DD format or an interval in the
                        "[+-]YyMmDd" format (with Y, M, and D numbers).
                        Defaults to today (2021-11-23).
  --timezone TIMEZONE, -t TIMEZONE
                        The timezone to display the hours in (e.g. 2 for UTC+2
                        or -3 for UTC-3). Can also be set in the
                        KOSMORRO_TIMEZONE environment variable.
  --no-colors           Disable the colors in the console.
  --output OUTPUT, -o OUTPUT
                        A file to export the output to. If not given, the
                        standard output is used. This argument is needed for
                        PDF format.
  --no-graph            Do not generate a graph to represent the rise and set
                        times in the PDF format.
  --debug               Show debugging messages

By default, only the events will be computed for today (Tuesday November 23,
2021). To compute also the ephemerides, latitude and longitude arguments are
needed.
"""


def test_run_without_argument():
    result = execute(KOSMORRO)
    assert result.is_successful()

    stdout = result.stdout.split("\n")
    assert_nb_lines(7, result.stdout)
    assert stdout[0] == date.today().strftime("%A %B %d, %Y")
    assert stdout[1] == ""

    moon_phase_line = re.compile(r"^Moon phase: ("
                                 r"(New Moon)|(Waxing Crescent)|"
                                 r"(First Quarter)|(Waxing Gibbous)|"
                                 r"(Full Moon)|(Waning Gibbous)|"
                                 r"(Last Quarter)|(Waning Crescent)"
                                 r")$")

    assert moon_phase_line.match(stdout[2])

    next_moon_phase_line = re.compile(r"^((New Moon)|(Waxing Crescent)|"
                                      r"(First Quarter)|(Waxing Gibbous)|"
                                      r"(Full Moon)|(Waning Gibbous)|"
                                      r"(Last Quarter)|(Waning Crescent)"
                                      r") "
                                      r"on ((Monday)|(Tuesday)|(Wednesday)|(Thursday)|(Friday)|(Saturday)|(Sunday)) "
                                      r"((January)|(February)|(March)|(April)|(May)|(June)|"
                                      r"(July)|(August)|(September)|(October)|(November)|(December)) "
                                      r"[0-9]{2}, [0-9]{4} at [0-9]{2}:[0-9]{2}$")

    assert next_moon_phase_line.match(stdout[3])
    assert stdout[4] == ""
    assert stdout[5] == "Note: All the hours are given in UTC."
