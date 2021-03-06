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
            logger.info('Dataframe will be written in the file "{}" (might be rewritten!).'.format(file_name),
                        created_by='system')
        return file_name

    def get_columns_names(self, strategy_name: str) -> (list, dict):
        """
        This function serves as column mapper for output file, with intention to change names of columns in final file.
        Function takes as a parameter name of the output strategy and if this format strategy exists, function iterates
        through its every item - column to be renamed. If parameter 'visible' of the column is set to 1, its
        'original_name' is added to list original_names and pair of key-value as 'original_name'-'final_name' is added
        to dictionary rename_names. This list and dictionary are in the end returned.

        :param str strategy_name: Name of the output strategy for dataframe. Contains list of columns to be renamed in
        output file.
        :return (list, dict): List with original names of columns and dictionary with original name as a key and final name as a
        value.
        """
        rename_names = {}

        for sv in self.config.get_attr('output_strategies')[strategy_name]:
            if sv.get('visible', 1) == 1:
                if 'original_name' not in sv or 'final_name' not in sv:
                    logger.warning('Items original_name or final_name are not in "{}" strategy.'.format(strategy_name),
                                   created_by='system')
                else:
                    rename_names[sv['original_name']] = sv['final_name']

        final_names = list(rename_names.keys())
        return final_names, rename_names
