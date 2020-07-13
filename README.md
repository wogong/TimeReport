# Time Report
Generating daily/weekly/monthly time report using [aTimeLogger](http://www.atimelogger.com) backend.

## Note
This repository is forked from [TimeReport](https://github.com/YujiShen/TimeReport).
Significant code changes as follows:
1. MySQL to sqlite3
2. Compatibility upgrade for Python 3 and Pandas
3. Remove Evernote support
4. Arguments interface update

Code has not been cleaned.

## Usage
- generate daily report
    - `python main.py -r -l 0` last day report
    - `python main.py -r 20200711`
## Introduction
### Stage
Early. In latest update, transform developing environment from Jupyter Notebook to PyCharm. Making it more like a program.

### Target User
It is highly customized, so currently only myself.

### Know Issue
* __Design__: This program is full of functions, without Object-Oriented Design. Next step is to learn and practice how to design this program in OOD.
* __Edit__: The whole database is based on data in aTimeLogger. Changes in local database will not affect remote data, and each time I change historical entries or types settings in aTimeLogger, I have to rebuild my local database.
* __Depth__: The analysis stays on descriptive level, need to dig deeper for more useful and hidden relations.

### Goal
My final goal is to build a webapp to replace aTimeLogger as my customized time tracking tool, for more flexibility to edit data and better integration with task management system. But this will not happen very soon, both my knowledge and time are not enough.

## Basic Flow
After retrieving all history data from aTimeLogger, building SQLite3 database.

Underlying procedures:

1. Get new data from aTimeLogger API, update database.
2. Utilize pandas, numpy to transform, aggregate, analyze data according to different time frame.
3. Draw plots and tables in matplotlib, save in files. See 'Gallery' for examples.

## Gallery
### Sleep Comparison Table
<p align="center"><img src="https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/sleep_table.png" width="600"></p>
Compare today's sleep status with yesterday, and its rank in last 7 days. Usually used in daily report.

### Task Table
<p align="center"><img src="https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/task_table.png" width="800"></p>

I use 'Comment' filed in aTimeLogger as Task or some activity I want to highlight, then aggregate its statistics everyday for morning review.

### Sleep Analysis
<p align="center"><img src="https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/sleep_plot.png" width="800"></p>

Analyze sleep conditions for weekly or monthly review. Inspired by app [Sleep Cycle](http://www.sleepcycle.com/start.html). In this picture (monthly report), X axis bottom is week number, top is month abbreviation.

### Group Pie Chart
<p align="center"><img src="https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/group_pie.png" width="800"></p>

Pie chart for each group to see total conditions. Mimic the pie chart in aTimeLogger, but add Average statistic.

### Type Descriptive Table
<p align="center"><img src="https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/type_table.png" width="800"></p>

Type detailed table replicate the 'Detail' function in aTimeLogger with a lot more statistics.

### Group Stacked Bar Chart
<p align="center"><img src="https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/group_bar.png" width="800"></p>

Stacked bar chart (horizontal) to see group trends inside a month or a week. Numbers in bar represents its percentage.

### Type Grid Stacked Bar Chart
<p align="center"><img src="https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/type_bar_grid.png" width="800"></p>

This 3x3 grid stacked bar chart (horizontal) to get the trends of each types in given time frame. Numbers in bar represents its hours.

### Aggregation Line Plot
<p align="center"><img src="https://raw.githubusercontent.com/YujiShen/TimeReport/master/images/type_line.png" width="800"></p>

A flexible plot to compare given types or groups in line plot.
