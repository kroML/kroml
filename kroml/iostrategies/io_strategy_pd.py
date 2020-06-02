import pandas as pd
import pickle
from iostrategies.abstract_pd_strategy import Strategy
from utils.logger import Logger

logger = Logger(__name__)


@logger.for_all_methods(in_args=True)
class IOStrategy(Strategy):
    def csv_load(self, input_file) -> dict:
        """
        Function loads CSV file, which name is stored in input_file's 'file_name', into dataframe.

        :param dict input_file: parameter containing key 'file_name' to recognize which file to load and key
                'original_names' to know which column to load.
        :return dict
        """
        return pd.read_csv(self.config.get_attr('input_directory') + input_file.get('file_name'),
                           usecols=input_file.get('original_names'), engine='python',
                           sep=input_file.get('separator', None))

    def csv_write(self, output_file) -> None:
        """
        Function saves dataframe into CSV file. Name of the dataframe is saved in output_file's 'df' and name
        of the final file is in output_file's 'file_name'.

        :param dict output_file: Dictionary where are stored details about output file, dataframe.
        :return None: No return value
        """
        output_file['df'].to_csv(output_file.get('file_name'), index=False, header=True,
                                 sep=output_file.get('separator', ','))

    def excel_load(self, input_file) -> dict:
        """
        Function loads Excel file, which name is stored in input_file's 'file_name' into dataframe.

        :param dict input_file: parameter containing key 'file_name' to recognize which file to load and key
                'original_names' to know which column to load.
        :return dict
        """
        if not input_file.get('sheet_name'):
            logger.warning('Sheet name was not specified. Using selected sheet.', created_by='system')

        return pd.read_excel(self.config.get_attr('input_directory') + input_file.get('file_name'),
                               sheet_name=input_file.get('sheet_name', 0), usecols=input_file.get('original_names'))

    def excel_write(self, output_file) -> None:
        """
        Function saves dataframe into Excel(.xlsx) file. Name of the dataframe is saved in output_file's 'df' and name
        of the final file is in output_file's 'file_name'.

        :param dict output_file: Dictionary where are stored details about output file, dataframe.
        :return None: No return value
        """
        output_file['df'].to_excel(output_file.get('file_name'), index=False, merge_cells=False)

    def pickle_load(self, input_file) -> dict:
        """
        Function loads Pickle file, which name is stored in input_file's 'file_name'.

        :param dict input_file: parameter containing file name to recognize which file to load.
        :return dict
        """
        return pickle.load(open(self.config.get_attr('input_directory') + input_file.get('file_name'), "rb"))

    def pickle_write(self, output_file) -> None:
        """
        Function saves dataframe into Pickle (.pickle) file. Name of the dataframe is saved in output_file's 'df'
        and name of the final file is in output_file's 'file_name'.

        :param dict output_file: Dictionary where are stored details about output file, dataframe.
        :return None: No return value
        """
        with open(output_file.get('file_name'), 'wb') as handle:
            pickle.dump(output_file['df'], handle)

    def graph_write(self, output_file):
        pass

    def load(self, input_file) -> None:
        '''
        Function loads file, which name and type is stored in input_file's 'file_name' into dataframe (name stored
        in input_file's 'variable_name') with or without renaming columns - according to 'format_strategy'.
        Dataframe is stored as object in variables with a key as input_file's 'variable_name'.
        :param dict input_file: Function takes as a parameter dictionary, that contains name of the file that should be
        loaded with a key 'file_name', a name of object where this file will be written with a key 'variable_name'
        and optional key 'format_strategy' where the value is a name of input strategy to be used to map column names.
        :return: None
        '''
        extension = self.get_file_extension(input_file)

        if self.type_dict.get(extension):
            if input_file.get('format_strategy') in self.config.get_attr('input_strategies'):
                original_names, rename_names = self.get_columns_names(input_file.get('format_strategy'))

                input_file['original_names'] = original_names
                df = self.__getattribute__(self.type_dict.get(extension)+'_load')(input_file)
                input_file.pop('original_names')

                df.rename(columns=rename_names, inplace=True)
            else:
                logger.warning(message='Strategy not found. Loading all columns.', created_by='system')
                df = self.__getattribute__(self.type_dict.get(extension)+'_load')(input_file)

            self.variables.set_object(key=input_file['variable_name'], obj=df)
        else:
            raise Exception('Extension of the file "{}" not recognized'.format(input_file.get('file_name')))

    def save(self, output_file) -> None:
        '''
        Method for choosing saving output file in corret type by choosing correct funtion according to file type.
        :param output_file: file dictionary containing information for choosing strategy.
        :return: None
        '''
        extension = self.get_file_extension(output_file)

        if self.type_dict.get(extension):
            file = {}
            file['file_name'] = self.config.get_attr('output_directory') + output_file.get('file_name')
            file['separator'] = output_file.get('separator', ',')

            if self.variables.get_object(key=output_file['variable_name']) is not None:
                if output_file.get('format_strategy') in self.config.get_attr('output_strategies'):
                    final_names, rename_names = super().get_columns_names(output_file.get('format_strategy'))
                    file['file_name'] = self.check_file_name(file['file_name'])

                    file['df'] = self.variables.get_object(key=output_file.get('variable_name')).rename(columns=rename_names)
                    file['df'] = file['df'][file['df'].columns.intersection(final_names)]
                else:
                    file['df'] = self.variables.get_object(key=output_file.get('variable_name'))

                self.__getattribute__(self.type_dict.get(extension)+'_write')(file)
            else:
                logger.warning('Required dataframe "{}" not found. Check variable_name in output_files and input_files '
                               'in utils/config/config.json'.format(output_file.get('variable_name')),
                               created_by='system')
        else:
            raise Exception('Extension of the file "{}" not recognized'.format(output_file.get('file_name')))