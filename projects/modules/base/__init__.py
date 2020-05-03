import abc


class Base(metaclass=abc.ABCMeta):
    def run(self, inputs):
        print("Module already run with input ", inputs)
