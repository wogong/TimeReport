"""This module perform operations about database."""
import mysql.connector
import sqlite3

def mysql_switch(onoff):
    """
    Turn on/off MySQL server.
    :param onoff: An integer 0 for Off, 1 for On
    """
    import subprocess
    if onoff == 0:
        print (subprocess.getstatusoutput("mysql.server stop"))
    elif onoff == 1:
        print (subprocess.getstatusoutput("mysql.server start"))


def connect_db_mysql():
    """Connect database and return connection, cursor."""
    config = {
      'user': 'wogong',
      'password': 'wogong_CC123',
      'host': '192.168.50.2',
      'database': 'time',
      'raise_on_warnings': True,
    }
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    return cnx, cursor


def connect_db(database='time.db'):
    """Connect database and return connection, cursor."""
    cnx = sqlite3.connect(database);
    cursor = cnx.cursor()
    return cnx, cursor


def empty_db(table='both', op='truncate'):
    """
    Empty time database for reconstruction.
    :param table: A string for table name in database. If 'both', empty all tables.
    :param op: A string to describe action type for emptying database, 'truncate' (default) or 'drop'.
    """
    cnx, cursor = connect_db()
    echo, query1, query2 = ("",)*3
    if op == 'truncate':
        query1 = "DELETE FROM intervals"
        query2 = "DELETE FROM types"
        echo = 'Database is truncated.'
    elif op == 'drop':
        query1 = 'drop table intervals'
        query2 = 'drop table types'
        echo = 'Database is dropped.'
    if table == 'both':
        cursor.execute(query1)
        cursor.execute(query2)
    elif table == 'intervals':
        cursor.execute(query1)
    elif table == 'types':
        cursor.execute(query2)
    cnx.commit()
    cnx.close()
    print (echo)


def create_types_table(database):
    """Create `types` table in database."""
    cnx, cursor = connect_db(database)
    create_types = ("create table types(\n"
                    "    guid char(36) not null,\n"
                    "    `group` tinyint(1) not null,\n"
                    "    `name` varchar(255) not null,\n"
                    "    parent char(36),\n"
                    "    `order` tinyint not null,\n"
                    "    color int not null,\n"
                    "    deleted tinyint(1) not null,\n"
                    "    revision int not null,\n"
                    "    imageId varchar(10) not null,\n"
                    "    primary key (guid)\n"
                    "    )")
    cursor.execute(create_types)
    cnx.commit()
    cnx.close()


def create_intervals_table(database):
    """Create `intervals` table in database."""
    cnx, cursor = connect_db(database)
    create_intervals = ("create table intervals(\n"
                        "    guid char(36) not null,\n"
                        "    type char(36) not null,\n"
                        "    `from` int(10) not null,\n"
                        "    `to` int(10) not null,\n"
                        "    delta MEDIUMINT not null,\n"
                        "    comment varchar(255),\n"
                        "    activityGuid char(36) not null,\n"
                        "    primary key (guid)\n"
                        "    )")
    cursor.execute(create_intervals)
    cnx.commit()
    cnx.close()


def create_all_tables(database):
    """Create all necessary tables in database"""
    create_types_table(database)
    create_intervals_table(database)


def insert_types(json):
    """
    Insert types data into database. Insertion will update existing data.
    :param json: A list of dict contain types data from aTimeLogger.
    """
    cnx, cursor = connect_db()
    for item in json:
        guid = '"%s"' % item['guid']
        group = 1 if item['group'] else 0
        name = '"%s"' % item['name']
        parent = '"%s"' % item['parent']['guid'] if item['parent'] else "NULL"
        order = item['order']
        color = item['color']
        deleted = 1 if item['deleted'] else 0
        revision = item['revision']
        image_id = '"%s"' % item['imageId']
        insert = "replace into types \
                (guid, `group`, `name`, parent, `order`, color, deleted, revision, imageId) \
                values ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})" \
                .format(guid, group, name, parent, order, color, deleted, revision, image_id)
        cursor.execute(insert)
        cnx.commit()
    cnx.close()


def insert_intervals(json):
    """
    Insert types data into database. Insertion will update existing data.
    :param json: A list of dict contain intervals data from aTimeLogger.
    """
    cnx, cursor = connect_db()
    for item in json:
        guid = '"%s"' % item['guid']
        type1 = '"%s"' % item['type']['guid']
        from1 = item['from']
        to = item['to']
        delta = item['to'] - item['from']
        comment = '"%s"' % item['comment'] if item['comment'] else "NULL"
        activity_guid = '"%s"' % item['activityGuid']
        insert = "replace into intervals \
                (guid, `type`, `from`, `to`, delta, `comment`, activityGuid) \
                values ({0}, {1}, {2}, {3}, {4}, {5}, {6})" \
                .format(guid, type1, from1, to, delta, comment, activity_guid)
        cursor.execute(insert)
        cnx.commit()
    cnx.close()


def insert_all(types, intervals):
    """
    Insert all data into database.
    :param types: A list of dict contain types data from aTimeLogger.
    :param intervals: A list of dict contain intervals data from aTimeLogger.
    """
    insert_types(types)
    insert_intervals(intervals)
