import numpy as np
import pandas as pd
from typing import Tuple
import datetime
import math
from collections import defaultdict
from manipulation.modules.outlier_detection.mapping import Mapping


def norm_date(column: pd.Series) -> pd.Series:
    """
    Return minmax of date column by number of days.
    :param pd.Series column: Input series with dates.
    :return pd.Series: Returns series with minmax numbers from 0 to 1 according to their weights.
    """
    timedelta = (column - datetime.datetime.now()).dt.days
    timedelta.name = column.name
    return minmax(timedelta)


def norm_cat(column: pd.Series) -> pd.Series:
    """
    Creates a matrix of all values in column, with 1 in a column with corresponding value in order.
    :param pd.Series column: Input data series with.
    :return pd.Series: Series with list for each row. 1 in a column with corresponding value, 0 when not right number.
    """
    columns = {}
    empty = [0] * len(column.unique())
    dummies = defaultdict(lambda: empty)
    for i, unique in enumerate(column.unique()):
        onehot = empty[:]
        onehot[i] = 1
        dummies[unique] = onehot
    columns[column.name] = dummies
    return column.apply(lambda x: columns[column.name][x])


def minmax(column: pd.Series) -> pd.Series:
    """
    From each value in column subtracts minimum number from column and then divide by maximum number.
    By doing so, it creates column with values in range from 0 to 1 according to previous rule, and with the biggest
    number as 1 and smallest number 0.
    :param pd.Series column: Input series of numbers.
    :return pd.Series: Series with numbers in range from 0 to 1 according to their weight.
    """
    columns = {}
    col_min = min(column.dropna())
    col_max = max(column.dropna())
    columns[column.name] = [col_min, col_max - col_min]
    return (column - columns[column.name][0]) / (columns[column.name][1])


def log_minmax(column: pd.Series):
    """
    Similar to minmax but with changes values logarithmically before executing minmax.
    :param pd.Series column: Input series of numbers.
    :return pd.Series: Series with numbers in range from 0 to 1 according to their weight.
    """
    columns = {}
    column = column.fillna(0)
    column = column.abs()
    column = np.log10(column)
    columns[column.name] = [min(column[column != -np.inf]), max(column)]
    column = column - columns[column.name][0]
    column = column.replace(-np.inf, 0)
    return column / (columns[column.name][1] - columns[column.name][0])


def nan_normalize(inp: np.ndarray) -> np.ndarray:
    """
    Normalizes the numpy array. (nan values in input array are allowed)

    :param numpy.ndarray inp: list or numpy array
    :return: numpy.ndarray -> returns normalized array
                     if the input is an array full of nans, original array is returned
    """

    if np.isnan(inp).all():
        return inp
    (inp_min, inp_max) = return_minmax(inp)
    if inp_min == inp_max:
        return inp - inp_min + 0.5
    return (inp - inp_min) / (inp_max - inp_min)


def return_minmax(inp: np.ndarray) -> Tuple[float, float]:
    """
    Returns minimum and maximum value of given array

    :param np.ndarray inp: list or numpy array
    :return: Tuple[float, float] -> returns minimum and maximum of input array
                         if the input is an array full of nans, nan values for minimum and maximum are returned
    """
    notnan_inp = inp[~np.isnan(inp)]
    if len(notnan_inp > 0):
        return notnan_inp.min(), notnan_inp.max()
    else:
        return np.nan, np.nan


def filter_months(dataframe: pd.DataFrame, number: int, column_name: str) -> pd.DataFrame:
    """
    Filters last x months from dataframe based on column 'column_name' of type datetime.

    :param pandas.DataFrame dataframe: dataframe including column 'RECONPERIOD_DATE'
    :param int number: number of last months to be filtered
    :param str column_name: name of the column we want to filter after

    :return: pandas.DataFrame -> returns filtered DataFrame containing last x months
                                 if number is greater than unique reconperiod dates, input dataframe is returned
                                 if number is less or equal to zero, empty dataframe is returned
    """
    if number <= 0:
        return dataframe.iloc[0:0]

    periods = dataframe[column_name].unique()
    periods = list(pd.to_datetime(periods))

    periods.sort()

    if number >= len(periods):
        return dataframe

    return dataframe[dataframe[column_name] >= periods[-number]]


def cut_months(dataframe: pd.DataFrame, current: str, column_name: str) -> pd.DataFrame:
    """
    Cut latest months if generating results for a reconperiod from past.

    :param pandas.DataFrame dataframe: dataframe including column 'column_name'
    :param str current: Current date.
    :param str column_name: Column with reckon period in datetime format %b-%Y.

    :return: pandas.DataFrame -> returns filtered DataFrame with current as the last reconperiod
    """
    current_date = datetime.datetime.strptime(current, '%b-%Y')

    if len(dataframe[dataframe[column_name] == current_date]) == 0:
        raise Exception('No records for current {} ('.format(column_name) + current + ')')

    return dataframe[dataframe[column_name] <= current_date]


def sort_dataframe(dataframe: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Sorts dataframe by values in columns in ascending order.

    :param pandas.DataFrame dataframe: dataframe
    :param list columns: list of columns to be sorted by from the highest to lowest priorities
    :return: pandas.DataFrame -> sorted dataframe
    """
    return dataframe.sort_values(by=columns).reset_index(drop=True)


def parse_date(string_date: str) -> datetime.datetime:
    """
    Parses input string of format 'MMM-yyyy' to datetime.

    :param str string_date: Date in string format 'MMM-yyyy'
    :return: datetime.datetime: parsed datetime

    """
    return datetime.datetime.strptime(string_date, '%b-%Y')


def not_empty_values(dataframe: pd.DataFrame, columns: list) -> pd.Series:
    """
    Returns one column with boolean value, if there is None, '0' or 0 in any column for given row, in the final column
    there will be False. If there is only valid value in a row for all dataframe columns (specified in variable columns)
    there will be True in given place in returning column.
    :param pd.DataFrame dataframe: Input dataframe, we are obtaining data from.
    :param columns: List of columns which are being checked for empty values.
    :return pd.Series: Column with result boolean values.
    """
    if len(columns) == 1:
        return ~(dataframe[columns[0]].isin(['0', 0])) & (dataframe[columns[0]].notnull())
    return ~(dataframe[columns[0]].isin(['0', 0])) & (dataframe[columns[0]].notnull()) & not_empty_values(dataframe,
                                                                                                          columns[1:])


def any_column_value(data: pd.DataFrame) -> pd.Series:
    """
    As a parameter takes dataframe and its last column, if there is value other than None or 0(zero), takes this value,
    otherwise function is looking in another columns in backward order for any other value other then these two and
    first found is a result for current row. If there is no other value as None or 0, then NaN is returned for row.
    :param pd.Dataframe data: Input dataframe, we are obtaining data from.
    :return pd.Series: Column with result values.
    """

    def recursion(columns: list):
        columns[0].name = 'a'
        if len(columns) != 1:
            columns[0].update(recursion(columns[1:]))
        return columns[0]

    return recursion([data[col].copy().replace(0, np.nan) for col in data.columns.tolist()])

# TODO Generalize and PEP8 these last 3 functions


def return_dates(dataframe):
    # Checks which columns in dataframe have type timestamp.
    def typefunc(item):
        return type(item)

    # vectorized funkcia sa opakuje, kym nepride k najmensiemu moznemu prvku, alebo cosi take ??
    # It does not seem to be working properly, not on my input dataframe, it gives str on columns with timestamp and datetime
    vectype = np.vectorize(typefunc)
    indexes = np.where(vectype(np.array(dataframe.columns)) == pd._libs.tslibs.timestamps.Timestamp)
    return dataframe.iloc[:, indexes[0][0]: indexes[0][-1] + 1]


def get_boundary(x, model, columns, boundary, boolean=False):
    if not boolean:
        # if any column is not of type string
        if any([type(x[y]) != str for y in columns]):
            # returns max boundary
            return math.inf * (boundary == 'max')
        # if all columns are str and boolean is false
        return model[boundary].get(tuple([x[y] for y in columns]), math.inf * (boundary == 'max'))
    if any([type(x[y]) != str for y in columns]):
        return False
    return model.get(tuple([x[y] for y in columns]), True)


def split_by_type(columns):
    cat, num, date, rest = [], [], [], []
    m = Mapping(None)
    for column in columns:
        if m[column] == 'cat':
            cat.append(column)
        elif m[column] is None:
            rest.append(column)
        elif 'num' in m[column]:
            num.append(column)
        elif m[column] == 'date':
            date.append(column)
        else:
            print('Something wrong with column types', column)
    return cat, num, date, rest
