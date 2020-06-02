import pandas as pd
import numpy as np
import scipy.stats as ss


def cramers_v(confusion_matrix: pd.DataFrame) -> int:
    """
    Calculate Cramers V statistic for categorial-categorial association.
    uses correction from Bergsma and Wicher,
    Journal of the Korean Statistical Society 42 (2013): 323-328

    :param confusion_matrix: Input table of values.
    :return: Correlation of values in input confusion_matrix. Close to 1 - strong association,
     close to 0 - weak association.
    """
    chi2 = ss.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    return np.sqrt(phi2corr / min((kcorr-1), (rcorr-1)))


def execute_cramers(input_df: pd.DataFrame, column: str, column_to_compare_with: str) -> int:
    """
    Function to execute Cramers V and check input variables.

    :param input_df: Dataframe, which function gets columns from.
    :param column: Name of the input column.
    :param column_to_compare_with: Name of the input column.
    :return: Calls cramers_v function and returns its return value.
    """
    if (isinstance(column_to_compare_with, str)) and (isinstance(column, str)):
        if (input_df.get(column) is not None) and (input_df.get(column_to_compare_with) is not None):
            confusion_matrix = pd.crosstab(input_df[column], input_df[column_to_compare_with]).as_matrix()
        else:
            raise Exception('Cannot execute Cramers V, because at least one of input columns does not exist.')
    else:
        raise Exception('Cannot execute Cramers V, because at least one input column has wrong variable type.')

    return cramers_v(confusion_matrix)
