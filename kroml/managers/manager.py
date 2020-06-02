import abc


class Manager(metaclass=abc.ABCMeta):
    """
    Abstract class from which inherits other manager classes. It contains __init__ method and abstract execute method.
    All manager subclasses are responsible for handling exceptions that occur during processing all of its subordinates.
    """

    def __init__(self, config, variables, error_handling='exit'):
        self.config = config
        self.variables = variables
        self.error_handling = error_handling

    @abc.abstractmethod
    def execute(self) -> None:
        pass
