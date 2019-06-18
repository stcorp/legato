from __future__ import absolute_import, division, print_function

_TRIGGERS = {}


def register(tpe, start, stop, join):
    def decorator(f):
        _TRIGGERS[tpe] = {
            "parser": f,
            "start": start,
            "stop": stop,
            "join": join,
            "threads": []
        }

        return f

    return decorator


def lookup(tpe):
    assert tpe in _TRIGGERS

    return _TRIGGERS[tpe]["parser"]


def start():
    for trigger in _TRIGGERS.values():
        trigger["threads"].append(trigger["start"]())


def stop():
    for trigger in _TRIGGERS.values():
        for thread in trigger["threads"]:
            if thread is not None:
                trigger["stop"](thread)
            else:
                trigger["stop"]()


def join():
    for trigger in _TRIGGERS.values():
        for thread in trigger["threads"]:
            if thread is not None:
                trigger["join"](thread)
            else:
                trigger["join"]()
