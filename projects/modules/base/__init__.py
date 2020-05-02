import abc


class Base(metaclass=abc.ABCMeta):
    def run(self, input):
        print("Module already run with input " + input)
