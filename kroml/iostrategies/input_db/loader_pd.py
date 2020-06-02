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

    def get_columns_names(self, strategy_name: str) -> (list, dict):
        """
        This function serves as column mapper for input file, with intention to change names of columns in final
        dataframe. Function takes as a parameter name of the input strategy and if this format strategy exists,
        function iterates through its every item - column to be renamed. If parameter 'visible' of the column is set to
        1, its 'original_name' is added to list original_names and pair of key-value as 'original_name'-'final_name'
        is added to dictionary rename_names. This list and dictionary are in the end returned.

        :param str strategy_name: Name of the input strategy for loaded file. Contains list of columns to be renamed.
        :return (list, dict): List with original names of columns and dictionary with original name as a key and final name as a
        value.
        """
        rename_names = {}

        for sv in self.config.get_attr('input_strategies')[strategy_name]:
            if sv.get('visible', 1) == 1:
                if 'original_name' not in sv or 'final_name' not in sv:
                    logger.warning('Items original_name or final_name are not in "{}" strategy.'.format(strategy_name),
                                   created_by='system')
                else:
                    rename_names[sv['original_name']] = sv['final_name']

        original_names = list(rename_names.keys())
        return original_names, rename_names
