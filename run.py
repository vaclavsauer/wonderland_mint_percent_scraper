#!/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime
import json
import logging
import os
import sqlite3
import time
import winsound

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

COUNTDOWN = 5
SKIP_WAIT = False
# SKIP_WAIT = True
SAVE_TO_DB = True
# SAVE_TO_DB = False

SCRAPED_POOLS = ["MIM", "TIME-MIM LP", "wETH.e"]
DB = "output.db"

con = sqlite3.connect(DB)


def alert(time_price, data):
    """
    Example alerts.json:
    {
        "AVAX": 5,  # %
        "MIM": 5,  # %
        "TIME-AVAX LP": 9.5,  # %
        "TIME-MIM LP": 5,  # %
        "PRICE ABOVE": 10000,  # USD
        "PRICE BELOW": 9000,  # USD
    }
    """

    try:
        with open(os.path.join(os.getcwd(), "alerts.json"), "r") as f:
            alerts = json.load(f)
    except Exception as e:
        alerts = {}
        logging.exception("\t❗️️ Can't load alerts")

    if "PRICE ABOVE" in alerts and time_price > alerts["PRICE ABOVE"]:
        winsound.Beep(400, 50)
        winsound.Beep(550, 50)
        winsound.Beep(700, 50)
        winsound.Beep(850, 50)
        time.sleep(1)

    if "PRICE BELOW" in alerts and time_price < alerts["PRICE BELOW"]:
        winsound.Beep(600, 50)
        winsound.Beep(500, 50)
        winsound.Beep(400, 50)
        winsound.Beep(300, 50)
        time.sleep(1)

    for mint in sorted(data):
        if mint not in alerts:
            continue

        if data[mint][1] > alerts[mint]:
            winsound.Beep(800, 200)
            time.sleep(0.05)
            winsound.Beep(900, 200)
            time.sleep(0.05)
            winsound.Beep(1000, 200)
            time.sleep(0.05)
            winsound.Beep(800, 200)

            time.sleep(1)


def run(driver):
    driver.refresh()

    # wait for page load
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".jss7 .choose-bond-view-card-metrics-value")
        )
    )

    treasury_balance = int(
        driver.find_element(
            By.CSS_SELECTOR, ".jss7 .choose-bond-view-card-metrics-value"
        )
        .text.replace(",", "")
        .replace("$", "")
    )
    time_price = float(
        driver.find_element(
            By.CSS_SELECTOR, ".jss8 .choose-bond-view-card-metrics-value"
        ).text.replace("$", "")
    )

    result = [
        f"{datetime.datetime.utcnow():%d.%m.%Y %H:%M:%S.%f}",
        treasury_balance,
        time_price,
    ]

    data = {}
    lines = driver.find_elements(By.CSS_SELECTOR, "tbody .MuiTableRow-root")
    for line in lines:
        line_values = line.find_elements(By.CSS_SELECTOR, ".bond-name-title")

        if line_values[0].text not in SCRAPED_POOLS:
            continue

        # remove "View Contract"
        if len(line_values) == 5:
            del line_values[1]

        try:
            mint = line_values[0].text  # 'TIME-MIM LP', 'MIM', 'wETH.e'
            price = float(line_values[1].text.split("\n")[-1:][0])  # '$\n8204.71'
            roi = float(line_values[2].text.replace("%", ""))  # '7.89%'
            purchased = int(
                line_values[3].text.replace(",", "").replace("$", "")
            )  # '$72,201,709'
        except Exception:
            print(
                f"ℹ️️{line_values[0].text}|{line_values[1].text}|{line_values[2].text}|{line_values[3].text}"
            )
            driver.save_full_page_screenshot(
                os.path.join(os.getcwd(), "last_error.png")
            )
            with open(
                os.path.join(os.getcwd(), "last_error.html"), "w", encoding="utf-8"
            ) as f:
                f.write(driver.page_source)
            raise

        data.update({mint: [price, roi, purchased]})

    for key in sorted(data):
        result += [
            "|",
            data[key][0],
            data[key][1],
            data[key][2],
        ]

    query_data = [(
        datetime.datetime.utcnow(),
        treasury_balance,
        time_price,

        # MIM
        data["MIM"][0],
        data["MIM"][1],
        data["MIM"][2],

        # TIME-MIM
        data["TIME-MIM LP"][0],
        data["TIME-MIM LP"][1],
        data["TIME-MIM LP"][2],

        # wETH.e
        data["wETH.e"][0],
        data["wETH.e"][1],
        data["wETH.e"][2],
    )]

    result = [str(r) for r in result]
    print("\t".join(result))

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
            time_mim_purchased, 

            weth_price, 
            weth_roi, 
            weth_purchased
            ) 
        values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    if SAVE_TO_DB:
        with con:
            con.executemany(sql, query_data)

    alert(time_price, data)


def get_sleep():
    now = datetime.datetime.utcnow()
    return 60.0 - now.second - now.microsecond / 1000000


def countdown(echo_time):
    if SKIP_WAIT:
        return

    sleep = get_sleep()

    print(f"⏳ Starting in {sleep:.1f} seconds...")

    if sleep > echo_time:
        time.sleep(sleep - echo_time)
    else:
        time.sleep(sleep % 1)

    sleep = get_sleep()
    while sleep > 1:
        print(f"⏳  {int(sleep) + 1}")
        time.sleep(sleep % 1)
        sleep = get_sleep()

    print(f"⏳  {int(sleep) + 1}")
    time.sleep(sleep % 1)
    print("Working... 💸💵💸")


# Welcome sound
print("❤️ Welcome ❤️")

# Load driver
print("Starting Firefox 🦊️")
options = FirefoxOptions()
# options.add_argument("--headless")

# This does not work
# service = Service('C:\\Program Files\\Mozilla Firefox\\firefox.exe')
# driver = webdriver.Firefox(service=service)

# This shows warning 🤷‍
driver = webdriver.Firefox(
    firefox_binary="C:\\Program Files\\Mozilla Firefox\\firefox.exe", options=options
)

driver.get("https://app.wonderland.money/#/mints")

# Wait for whole minute
countdown(5)

# Main loop
try:
    while True:

        # Fix having minimized window, where we can't get prices
        if driver.get_window_position()["x"] < 0:
            driver.maximize_window()

        for attempt in range(0, 3):
            try:
                run(driver)
                break
            except Exception as e:
                logging.exception("\t❗️️UPS ❗️️ 🙃")
                print(f"ℹ️️attempt #{attempt + 2}")

        time.sleep(
            60.0
            - datetime.datetime.utcnow().second
            + datetime.datetime.utcnow().microsecond / 1000000
        )
finally:
    driver.quit()
    driver.close()
