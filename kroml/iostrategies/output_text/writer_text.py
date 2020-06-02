import abc
from utils.logger import Logger
import os.path
import datetime

logger = Logger(__name__)


@logger.for_all_methods(in_args=False,
                        skip_func=['__init__'])
class Writer(metaclass=abc.ABCMeta):

    def __init__(self, config, variables, on_file_exist_rewrite=False):
        self.config = config
        self.variables = variables
        self.on_file_exist_rewrite = on_file_exist_rewrite

    @abc.abstractmethod
    def write(self, output_file: dict) -> None:
        pass

    def check_file_name(self, file_name: str) -> str:
        """
        Checks if file exists, according to 'on_file_exist_rewrite' rewrite file or create new with timestamp.
        If already exists file with same name and timestamp, function adds additional number in bracelets according to
        which file with same name in order it is.

        :param str file_name: Name of the file, that is being checked if already exists.
        :return string: Same name as input if file with this name does not exist
                        or new name for file, which is not used yet.
        """
        if os.path.isfile(file_name) and (self.on_file_exist_rewrite is False):
            now = (datetime.datetime.now()).strftime("%Y_%m_%d_%H-%M")
            parts = file_name.rpartition('.')
            file_name = parts[0] + now + parts[1] + parts[2]
            if os.path.isfile(file_name):
                counter = 0
                temp_file_name = file_name
                print(file_name)
                while os.path.isfile(temp_file_name):
                    temp_file_name = file_name
                    parts = temp_file_name.rpartition('.')
                    counter = counter + 1
                    temp_file_name = parts[0] + '(' + str(counter) + ')' + parts[1] + parts[2]
                    print(temp_file_name)
                file_name = temp_file_name
        else:
            logger.info('Text will be written in the file "{}" (might be rewritten!).'.format(file_name),
                        created_by='system')
        return file_name

