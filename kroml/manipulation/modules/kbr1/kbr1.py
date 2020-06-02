import pandas as pd
from manipulation.modules.abstract_module import Module
from utils.logger import Logger
import time


logger = Logger(__name__)


@logger.for_all_methods(in_args=True, skip_func=[])
class KBR1(Module):
    """
    KBR1 - Material deviation

    Predicts expected GL BALANCE USD for current month.
    """

    def execute(self, param: dict):
        """
        Default strategy - returns not processed dataframes with added blank columns

        :param dict param: Input parameters for execute function containing names of input and output datafranes.
        :return: pandas.DataFrame -> returns processed dataframe
        """

        input_df = param.get('input_df')
        In_Df = self.variables.get_object(input_df)
        logger.debug('test message')

        OutDf = pd.DataFrame()
        OutDf['REAL'] = ""
        OutDf['PREDICTION'] = ""
        self.variables.set_object("response", "KBR1-done")
        raise Exception("KBR1 module exception")

    def train(self, param: dict):
        logger.info('Hello')
        raise Exception('Just try')
