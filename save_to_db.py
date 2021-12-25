#!/usr/bin/python
# -*- coding: UTF-8 -*-

import csv
import sqlite3 as sl
from datetime import datetime

filename = "output.csv"
database = "output.db"

# os.remove(database)
con = sl.connect(database)
# with con:
#     con.execute("""
#         CREATE TABLE time_mint (
#             id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
#             timestamp TEXT,
#             treasury_balance INTEGER,
#             time_price INTEGER,
#             mim_price FLOAT,
#             mim_roi FLOAT,
#             mim_purchased INT,
#             time_mim_price FLOAT,
#             time_mim_roi FLOAT,
#             time_mim_purchased INT
#         );
#     """)


with con:
    con.execute(
        """
        ALTER TABLE time_mint ADD COLUMN weth_price FLOAT;
    """
    )
    con.execute(
        """
        ALTER TABLE time_mint ADD COLUMN weth_roi FLOAT;
    """
    )
    con.execute(
        """
        ALTER TABLE time_mint ADD COLUMN weth_purchased INT;
    """
    )

exit()

with con:
    con.execute(
        """
        DELETE FROM time_mint;
    """
    )

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
    with con:
        con.executemany(sql, data)
