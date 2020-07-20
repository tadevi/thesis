import abc


class ThreadTask(metaclass=abc.ABCMeta):

    def __init__(self, run=None, params=None):
        self._run = run
        self._params = params

    def run(self):
        if self._run is not None and self._params is None:
            self._run()
        elif self._params is not None:
            self._run(*self._params)


class ThreadTaskTerminate(ThreadTask):
    pass
