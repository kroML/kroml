import pandas as pd
import numpy as np
import keras
from sklearn.preprocessing import StandardScaler
from manipulation.modules.outlier_detection.mapping import Mapping

# TODO call_categorize and get_stats generalize and modify to work, to do so, you need to edit Mapping


def call_categorize(data, margin, train=False):
    data = data.copy()
    mapping = Mapping()
    for col in list(data.columns):
        if mapping[col] == 'date':
            if margin not in list(data.columns):
                print("Error")
            else:
                timedelta = (data[col] - data[margin]).dt.days
                timedelta.name = data[col].name
                data[col] = categorize(timedelta, train)
        elif mapping[col] == 'num1':
            data[col] = categorize(data[col], train)
    return data[list(set(data.columns) - set([margin]))]


def get_stats(stats):
    return stats


def categorize(num_input: pd.Series) -> pd.Series:
    """
    Divide values inside num_input into categories based on their average and standard deviation.
    :param pd.Series num_input: Input series of numerical values.
    :return pd.Series: Series with name of category instead of numerical value.
    """
    stats = {}
    stats[num_input.name] = {'mu': num_input.mean(), 'sigma': num_input.std()}
    mu = stats[num_input.name]['mu']
    sigma = stats[num_input.name]['sigma']
    stand = num_input - mu
    cats = pd.Series([''] * len(num_input), index=num_input.index)
    cats[np.abs(stand) <= 0.5 * sigma] = 's05'
    cats[(stand < -0.5 * sigma) & (stand >= -sigma)] = 'neg_s1'
    cats[(stand < -sigma) & (stand >= -2 * sigma)] = 'neg_s2'
    cats[(stand < -2 * sigma) & (stand >= -3 * sigma)] = 'neg_s3'
    cats[stand < -3 * sigma] = 'neg_s'
    cats[(stand > 0.5 * sigma) & (stand <= sigma)] = 'pos_s1'
    cats[(stand > sigma) & (stand <= 2 * sigma)] = 'pos_s2'
    cats[(stand > 2 * sigma) & (stand <= 3 * sigma)] = 'pos_s3'
    cats[stand > 3 * sigma] = 'pos_s'
    return cats


# categorical function for HBO, IF
def cat_to_num(mydf: pd.DataFrame) -> pd.DataFrame:
    """
    Function finds unique values for every item of every non-numerical column from input dataframe and creates a
    dictionary, where is stored this unique value and 0 if value is 0(NaN) or corresponding number - if its value was
    not in column yet, it will assign next number. Then the column(key) is replaced in dataframe with its value.
    :param  pd.DataFrame mydf: Input dataframe.
    :return  pd.DataFrame: Output dataframe with numbers instead of its values in columns.
    """
    dfp = mydf.copy()
    dfp = dfp.fillna(0)
    for col in mydf.columns:
        if mydf[col].dtypes == 'object':
            values = mydf[col].unique()
            n = 1
            dic = {}
            for i in values:
                if i != i or (i == 0):
                    dic[i] = 0
                else:
                    dic[i] = n
                    n = n + 1
                dfp[col] = dfp[col].replace(to_replace=i, value=dic[i])
    return dfp


# categorical funcion for PCA
def cat_to_num_scaled(mydf: pd.DataFrame) -> pd.DataFrame:
    """
    Function finds unique values for every item of every non-numerical column from input dataframe and creates a
    dictionary, where is stored this unique value and 0 if value is 0(NaN) or corresponding number - if its value was
    not in column yet, it will assign next number. Then the column(key) is replaced in dataframe with its value.
    At the end, function scale the output dataframe with StandardScaler's fit_transform function.
    :param  pd.DataFrame mydf: Input dataframe.
    :return  pd.DataFrame: Output dataframe with numbers instead of its values in columns.
    """
    dfp = mydf.copy()
    for col in mydf.columns:
        if mydf[col].dtypes == 'object':
            values = mydf[col].unique()
            n = 1
            dic = {}
            for i in values:
                if i != i or (i == 0):
                    dic[i] = 0
                else:
                    dic[i] = n
                    n = n + 1
                dfp[col] = dfp[col].replace(to_replace=i, value=dic[i])

    # rescale the output
    dfp = dfp.fillna(0)
    dfp = StandardScaler().fit_transform(dfp)
    dfp = pd.DataFrame(data=dfp, columns=mydf.columns)
    return dfp


def clas_num(myarray: np.ndarray) -> int:
    """
    Converting categorical data to 0 - 1 for SVM - one hot encoder. ????
    If there is 0 in array, returns length of array, else return length of array + 1.
    :param np.ndarray myarray: Input numpy array.
    :return int:
    """
    if 0 in myarray:
        return len(myarray)
    else:
        return len(myarray) + 1


def normal(myarray: np.ndarray) -> np.ndarray:
    """
    Normalization of current values in array. Replace values with their weights in interval 0..1.
    :param np.ndarray myarray: Input array.
    :return np.ndarray: Normalized array.
    """
    result = np.zeros(myarray.shape)
    imax = max(myarray)
    imin = min(myarray)
    for i in range(0, len(myarray)):
        result[i] = ((myarray[i] - imin) / (imax - imin))
    return result


def cat_to_vec(mydf: pd.DataFrame) -> np.ndarray:
    """
    Similar to cat_to_num, but also converts values into matrix with 1, when unique number corresponds and 0 when not.
    Same with non-object values.
    :param pd.DataFrame mydf: Input dataframe.
    :return np.ndarray:
    """
    dfp = mydf.copy()
    result = ''
    for col in mydf.columns:
        if mydf[col].dtypes == 'object':
            values = mydf[col].unique()
            n = 1
            dic = {}
            for i in values:
                if (i != i) or (i == 0):
                    dic[i] = 0
                else:
                    dic[i] = n
                    n = n + 1
                dfp[col] = dfp[col].replace(to_replace=i, value=dic[i])
            if result == '':
                result = keras.utils.to_categorical(dfp[col], num_classes=clas_num(dfp[col].unique()))
            else:
                add = keras.utils.to_categorical(dfp[col], num_classes=clas_num(dfp[col].unique()))
                result = np.concatenate((result, add), axis=1)
        else:
            dfp[col] = dfp[col].fillna(0)
            add = dfp[col].as_matrix()
            add = add.reshape(add.shape[0], 1)
            add = normal(add)
            if result == '':
                result = add
            else:
                result = np.concatenate((result, add), axis=1)
    return result
