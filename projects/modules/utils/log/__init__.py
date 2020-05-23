# all
LOG_MODE_VERBOSE = 0
# brief
LOG_MODE_INFO = 1

LOG_MODE_NONE = 2

log_mode = 1


def mode(mode: int):
    if mode in [LOG_MODE_VERBOSE, LOG_MODE_INFO, LOG_MODE_NONE]:
        global log_mode
        log_mode = mode


def v(tag, *args):
    if log_mode <= LOG_MODE_VERBOSE:
        print(tag, ":", *args)


def i(tag, *args):
    if log_mode <= LOG_MODE_INFO:
        print(tag, ":", *args)
