import threading
import time
import os
from datetime import datetime

from legato.registry import register
from legato.run import run_task

import schedule

import logging

_schedule = schedule.Scheduler()
logging.getLogger('schedule').propagate = False
logging.getLogger('schedule').addHandler(logging.NullHandler())


class Timer(threading.Thread):

    def __init__(self, schedule):
        super(Timer, self).__init__()
        self._schedule = schedule
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            self._schedule.run_pending()
            if self._schedule.next_run is not None:
                time.sleep(self._schedule.idle_seconds)
            else:
                time.sleep(60)


def start():
    thread = Timer(_schedule)
    thread.daemon = True
    thread.start()

    return thread


def stop(thread):
    thread.stop()


def join(thread):
    thread.join()

_intervals = ["second", "minute", "hour", "day", "week", "monday",
              "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
_units = ["seconds", "minutes", "hours", "days", "weeks"]


def parse_interval(parts, scheduler):
    part = parts.pop(0)

    if part in _intervals:
        interval = part

        # call scheduler.every().<interval>()
        return getattr(scheduler.every(), interval), parts
    else:
        try:
            n = int(part, 10)
            unit = parts.pop(0)
            assert unit in _units

            return getattr(scheduler.every(n), unit), parts
        except (AssertionError, ValueError) as e:
            raise AssertionError("expected a number followed by a unit or one of [%s] (%s)" % ("|".join(_intervals), e))


def parse_optional_at(parts, interval):
    if len(parts) == 0:
        return interval, parts
    else:
        assert len(parts) == 2, "Expected 'at HH:MM', got %s'" % " ".join(parts)
        at, time = parts
        assert at == "at", "Expected 'at HH:MM', got %s'" % " ".join(parts)

        return interval.at(time), parts


def parse_when(when, scheduler):
    parts = when.split(" ")
    assert len(parts) > 0, "Invalid time spec %s" % when

    every = parts.pop(0)
    assert every == "every", "Invalid time spec: %s" % when

    interval, parts = parse_interval(parts, scheduler)
    interval, parts = parse_optional_at(parts, interval)

    return interval


@register('time', start, stop, join)
def timed_trigger(job_name, when, **kwargs):
    parts = when.split(" ")
    assert len(parts) > 0, "Invalid time spec %s" % when
    parse_when(when, _schedule).do(run_task, job_name, **kwargs)
