import abc
from utils.logger import Logger

logger = Logger(__name__)


@logger.for_all_methods(in_args=False,
                        skip_func=['__init__'])
class Loader(metaclass=abc.ABCMeta):

    def __init__(self, config, variables):
        self.config = config
        self.variables = variables

    @abc.abstractmethod
    def load(self, input_file: dict) -> None:
        pass
