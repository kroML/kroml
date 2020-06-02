import pandas as pd
from managers.manager import Manager
from utils.logger import Logger
import pickle


class BatchManager(Manager):

    # TODO Make more abstract, make it usable
    """
      Splits input file into batches based on threshold how many rows can be in one batch.
      Batches are divided based on business units.
      Output of batch_manager is dictionary listing the business unit for each batch.
      Default threshold is 2 000 000 rows.
    """

    def division_to_batches(self, bu_row_count_dataframe, max_rows: int = 2000000, iter_part: int = 1,
                            part_prefix='part_') -> dict:

        # creating dictionary where each key is starting with "part_"
        bu_row_count_dataframe = bu_row_count_dataframe.sort_values([bu_row_count_dataframe.columns[1]],
                                                                    ascending=False)

        if bu_row_count_dataframe.iloc[0, 1] > max_rows:
            raise Exception('Cannot divide BUs to parts (biggest BU - {} rows, maximum allowed per part - {})'.format(
                bu_row_count_dataframe.iloc[0, 1], max_rows))

        df_dict = bu_row_count_dataframe.set_index(bu_row_count_dataframe.columns[0]).to_dict(orient='dict')[
            bu_row_count_dataframe.columns[1]]

        bu_dict = {}

        while df_dict != {}:
            cur_rows = 0
            bu_arr = []
            cur_part = part_prefix + str(iter_part)
            for i in list(df_dict.keys()):
                if df_dict[i] + cur_rows <= max_rows:
                    bu_arr += [i]
                    cur_rows += df_dict[i]
                    del df_dict[i]
                if cur_rows == max_rows:
                    break

            bu_dict[cur_part] = bu_arr

            iter_part += 1

        return bu_dict

    def execute(self):
        pass
