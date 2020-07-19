import abc


class Base(metaclass=abc.ABCMeta):
    def run(self, input):
      #  print("Module already run with input ", input)
        pass


class Filter(Base):
    def run(self, input) -> bool:
        super(Filter, self).run(input)
        return False


class Map(Base):
    def run(self, input):
        super(Map, self).run(input)
        return input