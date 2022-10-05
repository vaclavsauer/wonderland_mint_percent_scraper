#!/usr/bin/python
# -*- coding: UTF-8 -*-

import csv
import sqlite3 as sl
from datetime import datetime

filename = "output.csv"
database = "output.db"


def init_abracadabra_wmemo(connection):
    with connection:
        connection.execute("""
            CREATE TABLE abracadabra_wmemo (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                balance_mim FLOAT,
                balance_wmemo FLOAT,
                collateral_mim_amount FLOAT,
                collateral_expected_liquidation_price FLOAT,
                collateral_position_health FLOAT,
                position_collateral_deposited FLOAT,
                position_collateral_value FLOAT,
                position_your_position_apy FLOAT,
                position_mim_borrowed FLOAT,
                position_wmemo_liquidation_price FLOAT,
                position_memo_liquidation_price FLOAT,
                position_mim_left_to_borrow FLOAT,
                prices_memo_usd FLOAT,
                prices_memo_wmemo FLOAT,
                prices_wmemo_usd FLOAT
            );
        """)


def init_time_mint(connection):
    with connection:
        connection.execute("""
            CREATE TABLE time_mint (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                treasury_balance INTEGER,
                time_price INTEGER,
                mim_price FLOAT,
                mim_roi FLOAT,
                mim_purchased INT,
                time_mim_price FLOAT,
                time_mim_roi FLOAT,
                time_mim_purchased INT
            );
        """)


def add_new_columns(connection):
    with connection:
        connection.execute(
            """
            ALTER TABLE time_mint ADD COLUMN wmemo_mim_price FLOAT;
        """
        )
        connection.execute(
            """
            ALTER TABLE time_mint ADD COLUMN wmemo_mim_roi FLOAT;
        """
        )
        connection.execute(
            """
            ALTER TABLE time_mint ADD COLUMN wmemo_mim_purchased INT;
        """
        )


def clear(connection):
    with connection:
        connection.execute(
            """
            DELETE FROM time_mint;
        """
        )


def load_csv(connection):
    with open(filename) as f:
        reader = csv.reader(f)
        data = []
        for index, row in enumerate(reader):
            if index == 0:
                continue

            processed_row = (
                datetime.strptime(row[0], "%d.%m.%Y %H:%M:%S.%f"),
                int(row[1]),
                float(row[2]),
                # float(row[3]), # AVAX
                # float(row[4]),
                # int(row[5]),
                float(row[6]) if len(row) > 6 else None,  # MIM
                float(row[7]) if len(row) > 6 else None,
                int(row[8]) if len(row) > 6 else None,
                # float(row[9]), # TIME-AVAX
                # float(row[10]),
                # int(row[11]),
                float(row[12]) if len(row) > 6 else None,  # TIME-MIM
                float(row[13]) if len(row) > 6 else None,
                int(row[14]) if len(row) > 6 else None,
            )
            data += [processed_row]

        sql = """
            INSERT INTO time_mint (
                timestamp, 
                treasury_balance,            
                time_price, 
                
                mim_price, 
                mim_roi, 
                mim_purchased, 
                
                time_mim_price, 
                time_mim_roi, 
                time_mim_purchased) 
            values(?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        with connection:
            connection.executemany(sql, data)


# os.remove(database)
con = sl.connect(database)
load_csv(con)
