import pandas as pd
import numpy as np
from utils.logger import Logger
from utils.variable_context import VariableContext
from utils.training.normalization import nan_normalize, return_minmax

logger = Logger(__name__)


@logger.for_all_methods(in_args=True)
class KBR1_L5:
    """
    KBR1 - Material deviation

    Predicts expected GL BALANCE USD for current month.
    """

    def __init__(self, variable_manager: VariableContext):
        self.variables = variable_manager
        self.lg = Logger()

    def KBR1_predict(self, row: pd.Series) -> float:
        """
        Generates prediction on normalized for actual month using neural network model.
        Function takes in account:
            - GL BALANCE USD values from previous months
            - L5 attribute

        :param pandas.Series row: row of pivoted table with normalized GL Balance USD per reconperiod
        :return: float -> returns predicted value for actual month
        """

        # Creating an array as an input to neural network model
        s_row = row.to_string(index=False).replace(' ', '').replace('\n', ';')

        subset = s_row.split('NaN;')[-1].split('NaN')[-1]

        if subset == '':
            return np.nan

        subset = np.float_(subset.split(';'))

        # preparing encoded array using FRS Account
        if row.name[1] in self.variables.frs_dict:
            hot = self.variables.frs_dict[row.name[1]]
        else:
            hot = np.zeros(len(self.variables.frs_dict[list(self.variables.frs_dict.keys())[0]]), dtype=int)

        # repeating encoded array along axis
        hot = np.repeat([hot], len(subset), axis=0)

        # expanding GL Balance USD values array
        subset = np.expand_dims(subset, axis=1)

        # concatenation of 2 arrays above
        x_arr = np.concatenate((subset, hot), axis=1)

        # reshaping the array and returning predicted value
        if len(x_arr) >= 1:
            x_arr = np.expand_dims(x_arr, axis=0)
            return self.variables.model.predict(x_arr)[0, 0]
        else:
            return np.nan

    def execute(self, param: dict) -> pd.DataFrame:
        """
        Applying business requirenment - material deviation

        :param dict param: Dictionary of input parameters containing name of output dataframe.
            'REAL' .. real_column
            'PREDICTION' .. predict_column
            ['FRS_BUSINESS_UNIT', 'FRS_ACCOUNT', 'GL_ACCOUNT', 'CURRENCY_CODE'] .. merging_columns
        :return: pandas.DataFrame -> returns processed dataframe
        """
        OutDf = self.variables.get_object(param['output_df'])

        # preparing array as an input to predict fuction
        KBR1_break = self.variables.get_pivot_table()

        KBR1_break = KBR1_break.rename(columns={KBR1_break.columns[-1]: param['real_column']})
        KBR1_break_filter = KBR1_break.iloc[:, :-1]

        # intrapolate missing values
        KBR1_break_filter.interpolate(method='linear', axis=1, limit=2, limit_area='inside', inplace=True)

        KBR1_np = KBR1_break_filter.values

        # normalizing array
        KBR1_norm_np = np.apply_along_axis(nan_normalize, 1, KBR1_np)

        # preparing min and max values for de-normalization
        minmax_res = np.apply_along_axis(return_minmax, 1, KBR1_np)
        min_res = minmax_res[:, 0].reshape((len(minmax_res), 1))
        max_res = minmax_res[:, 1].reshape((len(minmax_res), 1))

        # creating normalized dataset
        KBR1_norm_df = pd.DataFrame(KBR1_norm_np, index=KBR1_break.index)

        # applying function to predict values
        KBR1_norm_df[param['predict_column']] = KBR1_norm_df.apply(self.KBR1_predict, axis=1)

        # de-normalizing dataset
        KBR1_denorm_df = pd.DataFrame(KBR1_norm_df.values * (max_res - min_res) + min_res, columns=KBR1_norm_df.columns)

        # adding 'PREDICTION' column to original dataframe
        KBR1_break[param['predict_column']] = KBR1_denorm_df[param['predict_column']].values
        # KBR1_break['PRED_OR_MEAN'] = KBR1_denorm_df['PRED_OR_MEAN'].values

        # preparing dataframe for joining with original dataframe
        KBR1_break_join = KBR1_break[~pd.isna(KBR1_break[param['real_column']])].reset_index()

        OutDf = OutDf.merge(KBR1_break_join, on=param['merging_columns'], how='left')

        return OutDf

    def train(self, param: dict):
        pass
