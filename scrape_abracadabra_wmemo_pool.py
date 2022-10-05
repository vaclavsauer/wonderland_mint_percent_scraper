#!/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime
import json
import logging
import re
import sqlite3
import time
from collections import OrderedDict

from config import FIREFOX_PROFILES_DIR, METAMASK_EXTENSION_URL, METAMASK_PWD

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


COUNTDOWN = 5  # seconds

SKIP_WAIT = False
# SKIP_WAIT = True

# SAVE_TO_DB = False
SAVE_TO_DB = True

DB = "output.db"
con = sqlite3.connect(DB)


def run(driver):
    scraped_data = OrderedDict()
    driver.refresh()

    # wait for page load
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".deposit-borrow-block"))
    )

    # Collateral
    collateral_values = driver.find_elements(
        By.CSS_SELECTOR, ".deposit-borrow-block .params-item"
    )

    for collateral_value in collateral_values:
        name = collateral_value.find_element(By.CSS_SELECTOR, "p:first-child").text
        value = float(
            collateral_value.find_element(By.CSS_SELECTOR, "p:last-child")
            .text.strip()
            .replace("$", "")
            .replace("~ ", "")
            .replace("%", "")
        )
        if name == "MIM Amount":
            scraped_data["collateral_mim_amount"] = value
        elif name == "Expected Liquidation Price":
            scraped_data["collateral_expected_liquidation_price"] = value
        elif name == "Position Health":
            scraped_data["collateral_position_health"] = value

    # Balances
    balances_values = driver.find_elements(
        By.CSS_SELECTOR, ".balances-block .balance-item"
    )

    for balances_value in balances_values:
        name = balances_value.find_element(By.CSS_SELECTOR, ".value-type").text
        value = float(
            balances_value.find_element(By.CSS_SELECTOR, ".value-text").text.strip()
        )

        if name == "wMEMO":
            scraped_data["balance_wmemo"] = value
        elif name == "MIM":
            scraped_data["balance_mim"] = value

    # Position
    position_values = driver.find_elements(
        By.CSS_SELECTOR, ".coll-params-block .param-item"
    )

    for position_value in position_values:
        name = position_value.find_element(By.CSS_SELECTOR, ".title").text
        value = float(
            position_value.find_element(By.CSS_SELECTOR, ".percent-text")
            .text.strip()
            .replace("$", "")
            .replace("%", "")
        )

        if name == "Collateral Deposited":
            scraped_data["position_collateral_deposited"] = value
        elif name == "Collateral Value":
            scraped_data["position_collateral_value"] = value
        elif name == "Your Position Apy":
            scraped_data["position_your_position_apy"] = value
        elif name == "MIM Borrowed":
            scraped_data["position_mim_borrowed"] = value
        elif name == "wMEMO Liquidation Price":
            scraped_data["position_wmemo_liquidation_price"] = value
        elif name == "MEMO Liquidation Price":
            scraped_data["position_memo_liquidation_price"] = value
        elif name == "MIM Left To Borrow":
            scraped_data["position_mim_left_to_borrow"] = value

    # Prices
    price_values = driver.find_elements(
        By.CSS_SELECTOR, ".coll-params-block .btm-text"
    )

    for price_value in price_values:
        value = price_value.text

        if re.match(r"1 MEMO = (.*) USD", value):
            scraped_data["prices_memo_usd"] = float(re.match(r"1 MEMO = (.*) USD", value)[1])
        elif re.match(r"1 MEMO = (.*) wMEMO", value):
            scraped_data["prices_memo_wmemo"] = float(re.match(r"1 MEMO = (.*) wMEMO", value)[1])
        elif re.match(r"1 wMEMO = (.*) MIM", value):
            scraped_data["prices_wmemo_usd"] = float(re.match(r"1 wMEMO = (.*) MIM", value)[1])

    query_data = [
        (
            datetime.datetime.utcnow(),
            scraped_data["balance_mim"] if "balance_mim" in scraped_data else None,
            scraped_data["balance_wmemo"] if "balance_wmemo" in scraped_data else None,
            scraped_data["collateral_mim_amount"] if "collateral_mim_amount" in scraped_data else None,
            scraped_data["collateral_expected_liquidation_price"] if "collateral_expected_liquidation_price" in scraped_data else None,
            scraped_data["collateral_position_health"] if "collateral_position_health" in scraped_data else None,
            scraped_data["position_collateral_deposited"] if "position_collateral_deposited" in scraped_data else None,
            scraped_data["position_collateral_value"] if "position_collateral_value" in scraped_data else None,
            scraped_data["position_your_position_apy"] if "position_your_position_apy" in scraped_data else None,
            scraped_data["position_mim_borrowed"] if "position_mim_borrowed" in scraped_data else None,
            scraped_data["position_wmemo_liquidation_price"] if "position_wmemo_liquidation_price" in scraped_data else None,
            scraped_data["position_memo_liquidation_price"] if "position_memo_liquidation_price" in scraped_data else None,
            scraped_data["position_mim_left_to_borrow"] if "position_mim_left_to_borrow" in scraped_data else None,
            scraped_data["prices_memo_usd"] if "prices_memo_usd" in scraped_data else None,
            scraped_data["prices_memo_wmemo"] if "prices_memo_wmemo" in scraped_data else None,
            scraped_data["prices_wmemo_usd"] if "prices_wmemo_usd" in scraped_data else None,
        )
    ]

    print(
        "{} | {} | {} | {} | {}".format(
            str(query_data[0][0]),
            "\t".join(str(i) for i in query_data[0][1:3]),
            "\t".join(str(i) for i in query_data[0][3:6]),
            "\t".join(str(i) for i in query_data[0][6:13]),
            "\t".join(str(i) for i in query_data[0][13:])
        )
    )

    sql = """
        INSERT INTO abracadabra_wmemo (
            timestamp,
            balance_mim,
            balance_wmemo,
            collateral_mim_amount,
            collateral_expected_liquidation_price,
            collateral_position_health,
            position_collateral_deposited,
            position_collateral_value,
            position_your_position_apy,
            position_mim_borrowed,
            position_wmemo_liquidation_price,
            position_memo_liquidation_price,
            position_mim_left_to_borrow,
            prices_memo_usd,
            prices_memo_wmemo,
            prices_wmemo_usd
        ) 
        values(?, ?, ?,?, ?, ?,?, ?, ?,?, ?, ?,?, ?, ?, ?);
    """

    if SAVE_TO_DB:
        with con:
            con.executemany(sql, query_data)


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


# -------------------------------------
# --- RUN -----------------------------
# -------------------------------------

print("❤️ Welcome ❤️")

# Load driver
print("Starting Firefox 🦊️")
options = FirefoxOptions()
options.add_argument("-profile")
options.add_argument(FIREFOX_PROFILES_DIR)

driver = Firefox(options=options)

with open('session', 'w') as f:
    f.write(json.dumps({
        "session_id": driver.session_id,
        "url": driver.command_executor._url,
    }))

# log in to metamask
print("Initializing Metamask 🦊")
driver.get(METAMASK_EXTENSION_URL)
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#password"))
)
driver.find_element(By.CSS_SELECTOR, "#password").send_keys(METAMASK_PWD)
driver.find_element(By.CSS_SELECTOR, "button").click()
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".wallet-overview"))
)

print("Loading https://abracadabra.money/pool/5")
driver.get("https://abracadabra.money/pool/5")

print("Done")
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
            - datetime.datetime.utcnow().microsecond / 1000000
        )
finally:
    driver.quit()
    driver.close()
