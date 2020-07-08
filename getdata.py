"""This module are functions for retrieving data from database and transform to desired format."""
from time_func import *
from db import connect_db
import numpy as np
import pandas as pd


def get_sleep_data(start, end):
    """
    Get sleep entries from data base from 'start' to 'end'.
    :param start: (int) unix timestamp for start point.
    :param end: (int) unix timestamp for end point.
    :return: a list of tuples (start, end, duration).
    """
    cnx, cursor = connect_db()
    query = """select "from" as _if, "to" as _it, delta
            from types, intervals
            where intervals.type = types.guid and
            types.name = 'S1:Sleep' and
            _it > {0} and
            _it < {1}
            order by _it""".format(start, end)
    cursor.execute(query)
    sleep_entries = cursor.fetchall()
    cnx.close()
    return sleep_entries


def get_sleep_dataframe(start, end):
    """
    Get sleep duration and its date, from 'start' to 'end'. Durations are aggregated by date.
    'from' time before 19 will be consider for same day, otherwise to next day.
    :param start: (int) unix timestamp for start point.
    :param end: (int) unix timestamp for end point.
    :return: a DataFrame with column (date) date, (int) delta
    """
    entries = get_sleep_data(start, end)
    dataframe = pd.DataFrame(entries, columns=['from', 'to', 'delta'])
    dataframe['date'] = dataframe['from'].apply(
        lambda x: ts2date(ts2datetime(x).shift(days=1)) if ts2datetime(x).hour >= 19 else ts2date(x))

    # aggregate duplicate date duration
    agg_duration = dataframe[['delta', 'date']].groupby('date').aggregate(np.sum)
    agg_duration.reset_index(inplace=True)

    # remove duplicates and keep later timestamp
    dataframe = dataframe[~dataframe.duplicated('date', keep='last')][['from', 'to', 'date']]
    dataframe = dataframe.merge(agg_duration, on="date")
    dataframe = dataframe.reindex()
    return dataframe


def get_data(start, end):
    cnx, cursor = connect_db()
    query = """select "from" as _if, "to" as _it, delta, a.name, comment
            from types a, intervals
            where intervals.type = a.guid and
            _it > {0} and
            _if < {1}
            order by _it""".format(start, end)
    cursor.execute(query)
    entries = cursor.fetchall()
    cnx.close()
    return entries


def get_dataframe(start, end):
    data = get_data(start, end)
    data_group_added = []
    group_dict = {
        'S1': 'Sleep',
        'S2': 'Work',
        'S3': 'Develop',
        'S4': 'Maintain',
        'S5': 'Entertain',
    }
    for item in data:
        item_list = list(item)
        group = group_dict[item[3][:2]]
        item_list.append(group)
        data_group_added.append(item_list)
    dataframe = pd.DataFrame(data_group_added, columns=['from', 'to', 'delta', 'type', 'comment', 'group'])
    return dataframe


def get_cut_dataframe(start, end):
    """
    Cut first and last row in dataframe into start and end time.
    :param start: (int) unix timestamp for start point.
    :param end: (int) unix timestamp for end point.
    :return: (DataFrame)
    """
    data = get_dataframe(start, end)
    nrow = data.shape[0]
    data.loc[0, 'from'] = start
    data.loc[0, 'delta'] = data.loc[0, 'to'] - start
    if data.loc[nrow-1, 'to'] > end:
        data.loc[nrow-1, 'to'] = end
        data.loc[nrow-1, 'delta'] = end - data.loc[nrow-1, 'from']
    return data


# TODO delete get_cut_day_dataframe() when safe
def get_cut_day_dataframe(start, end):
    """
    Cut all cross-day rows in dataframe into two rows for two days.
    :param start: (int) unix timestamp for start point.
    :param end: (int) unix timestamp for end point.
    :return: (DataFrame)
    """
    entries = get_dataframe(start, end)
    data = entries.copy()
    data['datetime'] = data['to'].map(ts2date)

    point = arrow.Arrow.range('day', ts2datetime(start), ts2datetime(end))
    point = [x.timestamp for x in point]
    ind = 0
    newRow = 0
    for index, row in entries.iterrows():
        if row['to'] == point[ind]:
            ind += 1
        elif row['from'] < point[ind] < row['to']:
            if index == 0:
                data.loc[0, 'from'] = start
                data.loc[0, 'delta'] = data.loc[0, 'to'] - data.loc[0, 'from']
            elif index == len(entries)-1:
                data.loc[data.index[-1:], 'to'] = end
                data.loc[data.index[-1:], 'delta'] = data.loc[data.index[-1:], 'to'] - data.loc[data.index[-1:], 'from']
                data.loc[data.index[-1:], 'datetime'] = ts2date(data.loc[data.index[-1:], 'from'])
                break
            else:
                row = entries.iloc[[index]].copy()
                row.loc[index, 'delta'] = abs(point[ind]-row.loc[index, 'from'])
                row.loc[index, 'to'] = point[ind]
                row.loc[index, 'datetime'] = ts2date(row.loc[index, 'from'])
                newInd = index + newRow
                data.loc[newInd, 'delta'] = abs(point[ind]-data.loc[newInd, 'to'])
                data.loc[newInd, 'from'] = point[ind]
                data = pd.concat([data[:newInd], row, data[newInd:]])
                data = data.reset_index(drop=True)
                newRow += 1
            ind += 1
        if ind >= len(point):
            break
    data['datetime'] = data['from'].map(ts2datetime)
    return data


def get_cut_level_dataframe(start, end, level):
    """
    Cut all cross-day rows in dataframe into two rows for two days.
    :param level: (int) time frame number
    :param start: (int) unix timestamp for start point.
    :param end: (int) unix timestamp for end point.
    :return: (DataFrame)
    """
    entries = get_cut_dataframe(start, end)
    data = entries.copy()
    break_point = break_level(start, end, level)
    if len(break_point) != 0:
        data['datetime'] = data['to'].map(ts2date)

        ind = 0
        new_row = 0
        for index, row in entries.iterrows():
            if row['to'] == break_point[ind]:
                ind += 1
            elif row['from'] < break_point[ind] < row['to']:
                row = entries.iloc[[index]].copy()
                row.loc[index, 'delta'] = abs(break_point[ind]-row.loc[index, 'from'])
                row.loc[index, 'to'] = break_point[ind]
                row.loc[index, 'datetime'] = ts2date(row.loc[index, 'from'])
                new_ind = index + new_row
                data.loc[new_ind, 'delta'] = abs(break_point[ind]-data.loc[new_ind, 'to'])
                data.loc[new_ind, 'from'] = break_point[ind]
                data = pd.concat([data[:new_ind], row, data[new_ind:]])
                data = data.reset_index(drop=True)
                new_row += 1
                ind += 1
            if ind >= len(break_point):
                break

    data['datetime'] = data['from'].map(ts2datetime)
    data['date_agg'] = data['from'].map(lambda x: ts2str_level(x, level))
    return data


def get_group_order():
    """Return group order in dataframe."""
    cnx, cursor = connect_db()
    query = """select name, `order` from types where `group`=1"""
    cursor.execute(query)
    result = cursor.fetchall()
    result = pd.DataFrame(result, columns=['group', 'order'])
    cnx.close()
    return result


def get_type_order(group):
    """Return group order in dataframe.
    :param group: str, group name
    """
    cnx, cursor = connect_db()
    query = """select a.name, a.`order` from types a, types b
            where a.parent=b.guid and
            b.name='{0}'""".format(group)
    cursor.execute(query)
    result = cursor.fetchall()
    result = pd.DataFrame(result, columns=['type', 'order'])
    cnx.close()
    return result


def get_all_types():
    """Return all types name and order in dataframe."""
    cnx, cursor = connect_db()
    query = """select a.name, b.`order` from types a, types b
            where a.parent=b.guid"""
    cursor.execute(query)
    result = cursor.fetchall()
    result = pd.DataFrame(result, columns=['type', 'order'])
    cnx.close()
    return result
