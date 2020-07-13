"""Main module to combine functions into complete services"""

from db import *
from note import *
from time_api import *
from plot_func import *
import argparse
import os
import sys


def update_db():
    """Insert last two days' entries in aTimeLogger into database."""
    auth_header = get_auth_header()
    new_entries = get_new_intervals(auth_header)
    insert_intervals(new_entries)
    print ("Update complete!")


def rebuild_table(table):
    """
    Empty all entries in passed table and reinsert current data into table.
    This function is used when history or types are edited.
    :param table: A string of table name in database, 'types' or 'intervals'
    """
    empty_db(table)
    auth_header = get_auth_header()
    echo = 'Please correct your table name!'
    if table == 'types':
        types = get_types(auth_header)
        insert_types(types)
        echo = "Rebuild types complete!"
    elif table == 'intervals':
        intervals = get_all_intervals(auth_header)
        insert_types(intervals)
        echo = "Rebuild intervals complete!"
    print (echo)


def rebuild_db(op='truncate'):
    """
    Rebuild the whole database.
    :param op: the option when empty the database, 'truncate' (default) or 'drop'
    """
    if op == 'truncate':
        empty_db()
    else:
        empty_db(op=op)
        create_all_tables()
    auth_header = get_auth_header()
    types = get_types(auth_header)
    intervals = get_all_intervals(auth_header)
    insert_all(types, intervals)
    print ("Rebuild database complete!")


def daily_report(date=None):
    """
    Generate daily report in Evernote.
    Report content: 1.Date info, 2.Sleep table, 3.Group pie chart, 4.Task table.
    :param date: A string of date in the format 'YYYYMMDD', default None for yesterday.
    """
    if date:
        start, end = str2level_range(date, 0)
        date_info = day_info(date)
    else:
        # TODO Replace human_qr with str2level_range
        start, end = human_qr('last 1 days')
        date_info = day_info()
    title = ts2str_level(start, 0)
    # sleep_data = sleep_compare(date)
    # sleep_table_plot(sleep_data, date)
    last_cut = get_cut_level_dataframe(start, end, 0)
    group_pie_plot(last_cut, date)
    task_data = get_task_table(last_cut)

    # in case of early date with zero task
    if task_data.shape[0] != 0:
        task_table_plot(task_data)

    print ("Generate daily report for {0}!".format(title))


def weekly_report(week=None):
    """
    Generate weekly report in Evernote.
    Report content: 1.Group pie chart, 2.Type table, 3.Group stacked bar chart, 4. Type grid chart, 5. Sleep plot.
    :param week: A string of week number in the format 'YYYYWww', e.g '2015W07'. Default None for last week.
    """
    if week:
        start, end = str2level_range(week, 1)
    else:
        now = arrow.get(datetime.now(), 'Asia/Shanghai')
        start, end = str2level_range(now.strftime('%YW%V'), 1)
    start_date = ts2datetime(start).strftime('%b %d')
    end_date = ts2datetime(end-1).strftime('%b %d')
    title = ts2datetime(start).strftime("%Y Week%V ({0} - {1})".format(start_date, end_date))

    cut_data = get_cut_dataframe(start, end)
    group_pie_plot(cut_data, week)
    # type_data = get_type_detail(cut_data)
    # type_table_plot(type_data)
    # agg_data_group = agg_level(start, end, 'group', 0)
    # group_barh_plot(agg_data_group, 0)
    # agg_data_type = agg_level(start, end, 'type', 0)
    # type_bar_grid_plot(agg_data_type, 0)
    sleep_data = get_sleep_dataframe(start, end)
    sleep_plot(sleep_data)

    print ("Generate weekly report for {0}!".format(title))


def monthly_report(month=None):
    """
    Generate monthly report in Evernote.
    Report content: 1.Group pie chart, 2.Type table, 3.Group stacked bar chart, 4. Type grid chart, 5. Sleep plot.
    :param month: A string of month number in the format 'YYYYMmm', e.g '2015M02'. Default None for last month.
    """
    if month:
        start, end = str2level_range(month, 2)
    else:
        now = arrow.get(datetime.now(), 'Asia/Shanghai')
        start, end = str2level_range(now.strftime('%YM%m'), 2)
    start_week = ts2datetime(start).strftime('%V')
    end_week = ts2datetime(end-1).strftime('%V')
    title = ts2datetime(start).strftime("%Y Month%m (W{0} - W{1})".format(start_week, end_week))
    tags = date_tag(start, 2)

    cut_data = get_cut_dataframe(start, end)
    group_pie_plot(cut_data, month)
    # type_data = get_type_detail(cut_data)
    # type_table_plot(type_data)
    # agg_data_group = agg_level(start, end, 'group', 1)
    # group_barh_plot(agg_data_group, 1)
    # agg_data_type = agg_level(start, end, 'type', 1)
    # type_bar_grid_plot(agg_data_type, 1)
    sleep_data = get_sleep_dataframe(start, end)
    sleep_plot(sleep_data)

    print ("Generate monthly report for {0}!".format(title))


def gen_report(level=0, date=None):
    """
    Report wrapper function.
    :param level: An integer for different time levels. 0: daily (default), 1: weekly, 2: monthly.
    :param date: A string to specify date/week/month.
    """
    if level == 0:
        daily_report(date)
    elif level == 1:
        weekly_report(date)
    elif level == 2:
        monthly_report(date)


def test_func():
    """Test function"""
    # start, end = human_qr('last 1 week')
    # cut_data = get_cut_dataframe(start, end)
    # group_pie_plot(cut_data)
    # day_cut_data = get_cut_day_dataframe(start, end)
    # agg_data = agg_level(start, end, 'type', 0)
    # types = get_type_order('Health').type
    # agg_line_plot(agg_data, 'type', 0, lst=types, smooth=False)
    # sleep_data = get_sleep_dataframe(start, end)
    # sleep_plot(sleep_data)
    # agg_data = agg_level(start, end, 'group', 0)
    # group_barh_plot(agg_data, 0)
    # agg_data = agg_level(start, end, 'type', 0)
    # type_bar_grid_plot(agg_data, 0)
    weekly_report("2015W48")


def main():
    # Add argument to program for more flexible console control
    parser = argparse.ArgumentParser(description='Report system actions.')
    parser.add_argument("-d", "--database", default='time.db',  help="dababase file")
    parser.add_argument("-u", "--update", help="update database", action="store_true")
    parser.add_argument("-c", "--construct", help="construct database", action="store_true")
    parser.add_argument("-r", "--report", help="time logging report", action="store_true")
    parser.add_argument("-l", "--level", type=int, default=0, choices=[0, 1, 2],
                        help="choose the report level (default: 0)")
    parser.add_argument("-t", "--time", help="specify date/week/month for report. "
                                             "Day: '19970215'; Week: '1999W05'; Month: '2010M02'")
    args = parser.parse_args()
    if not os.path.exists(args.database):
        print ('no database file found, creating database.')
        create_all_tables(args.database)

    if args.update:
        update_db()

    if args.construct:
        rebuild_db()

    if args.report:
        update_db()
        gen_report(args.level, args.time)


if __name__ == '__main__':
    sys.settrace
    main()
