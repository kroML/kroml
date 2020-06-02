import pandas as pd
import numpy as np


class Materiality:
    """
        - Add BU to dataframe
        - Create Materiality buckets
        - Add score
    """

    def create_rubrics(self, df: pd.DataFrame, group_by_column: str, index_column: str, merge_column: str,
                       round_to=-4) -> pd.DataFrame:
        """
        Create rubrics dataframe.
        :param df: Input dataframe.
        :param group_by_column: Name of the column in input dataframe we are going to group by.
        :param index_column: Name of column in dataframe for indexing.
        :param merge_column: Name of column we are going to merge with.
        :param round_to:
        :return:
        """
        # df_4A = self.create_4A(df_raw)
        # Can go into Variable manager?
        perc_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        # create scoring rubrics
        df_score_rubrics = df.groupby(group_by_column).quantile(perc_list).unstack()
        df_score_rubrics.columns = df_score_rubrics.columns.droplevel(level=0)
        # round to 10K
        df_score_rubrics = df_score_rubrics.round(round_to)  # why to round??
        df_score_rubrics[index_column] = df_score_rubrics.index
        df_score_rubrics = df_score_rubrics.merge(df[[group_by_column, merge_column]].drop_duplicates(),
                                                  how='left', left_on=index_column, right_on=group_by_column)
        df_score_rubrics.rename(columns={merge_column: 0.0}, inplace=True)
        df_score_rubrics = df_score_rubrics[[index_column, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]]
        return df_score_rubrics

    def create_dict(self, df_score_rubrics: pd.DataFrame, index_column: str) -> (dict, dict):
        """
        Creates two dictionaries, one with index_column as a key and all other columns as a list of values and second
        with index_column as a key and list of numbers 0.0, 0.1, .. 1.0 as a value.
        :param df_score_rubrics: Input dataframe.
        :param index_column: Column in dataframe for indexing.
        :return: Returns two dictionaries with index_column as a key and other columns and list of numbers 0.0, 0.1, ..
        1.0 as values.
        """
        # bounds dict - df to dict
        boundsdict = df_score_rubrics.set_index(index_column).T.to_dict('list')

        # score dict
        BU_List = df_score_rubrics[index_column].tolist()
        scoredict = dict.fromkeys(BU_List, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
                                            1.0])  # includes score of 1.0 in case there are no matches in bounds list
        return boundsdict, scoredict

    def apply_rubric(self, df_4A: pd.DataFrame, df_score_rubrics: pd.DataFrame, index_column: str, balances_column: str,
                     business_unit_column: str) -> pd.DataFrame:
        """
        Applies rubric on input dataframe, creates new column with scores.

        :param df_4A: Input dataframe.
        :param df_score_rubrics: Rubrics dataframe.
        :param index_column: Index column for rubrics dataframe.
        :param balances_column: Name of column with balances in input dataframe.
        :param business_unit_column: Name of business unit column in input dataframe.
        :return: Input dataframe, that involves new column with scores after rubric was applied.
        """
        # take balances as inputs
        input_bal = np.expand_dims(df_4A[balances_column].values, axis=1)
        boundsdict, scoredict = self.create_dict(df_score_rubrics, index_column)

        # create bounds/scores list
        try:
            bounds = np.array(list(df_4A[business_unit_column].apply(
                lambda x: list(boundsdict.get(x, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])))))  # , boundsdict['default']
            scores = np.array(list(df_4A[business_unit_column].apply(
                lambda x: list(scoredict.get(x, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])))))  # , boundsdict['default']
        except Exception as e:
            print('ERROR {} in boundsdict or scoredict:'.format(e))
            print("Dict boundsdict:", boundsdict.keys())
            print("Dict scoredict:", scoredict.keys())
            print("DF:", df_4A[business_unit_column].unique())
            raise e
        # get score
        indexes = np.argmax(
            np.concatenate((bounds - input_bal >= 0, np.expand_dims(np.ones(input_bal.shape[0]), axis=1)), axis=1),
            axis=1)

        df_4A['MATERIALITY_SCORE'] = scores[np.arange(input_bal.shape[0]), indexes]
        return df_4A
