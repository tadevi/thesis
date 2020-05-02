from modules.base import Base


class Main(Base):
    def __init__(self, configs):
        self.configs = configs

    def run(self, input):
        super(Main, self).run(input)
