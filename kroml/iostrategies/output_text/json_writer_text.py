from iostrategies.output_db.writer_pd import Writer
from utils.logger import Logger
import datetime
import json

logger = Logger(__name__)

@logger.for_all_methods(in_args=False,
                        skip_func=['__init__'])
class JSONWriter(Writer):

    def write(self, output_file: dict) -> None:
        """
        Function saves dictionary with text into JSON(.json) file. Name of the text-JSON is saved in output_file's 'variable_name'
        and name of the final file is in output_file's 'file_name'. Optional format_strategy.

        :param dict output_file: Dictionary where are stored details about output file, dataframe and strategy.
        :return None: No return value
        """
        file_name = self.config.OUTPUT_DIRECTORY + output_file.get('file_name')

        if self.variables.get_object(key=output_file.get('variable_name')) is not None:
            output_file_dict = self.variables.get_object(key=output_file.get('variable_name'))
            with open(file_name, 'w') as json_file:
                json.dump(output_file_dict, json_file)  # TO DO: encode properly all characters
        else:
            logger.warning('Required dict-text "{}" not found. Check variable_name in output_files and input_files '
                           'in utils/config/config.json'.format(output_file.get('variable_name')), created_by='system')
