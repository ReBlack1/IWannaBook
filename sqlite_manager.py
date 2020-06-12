#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
import sqlite3
import time
import os.path


def get_connection(db_path):
    """
    :param db_path: string, xxx.db
    :return: connection for other functions
    """
    return sqlite3.connect(db_path)


def add_string(connection, table_name, values):
    """
    :param connection: from get_connection func (optimisation)
    :param table_name:
    :param values: list or tuple
    :return:
    """
    cursor = connection.cursor()
    cursor.execute('INSERT INTO %s VALUES (%s)' % (table_name, ','.join('?' * len(values))), values)
    connection.commit()


def get_id_loading_book(conn):
    """

    :param conn: from get_connection func (optimisation)
    :return:
    """
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM BookAtribute WHERE loading = 1 AND link IS NULL ')
    conn.commit()
    rows = cursor.fetchall()
    return rows
