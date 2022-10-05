#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config
from base import WanderBase


class TimeAutoClaim(WanderBase):
    connection = sqlite3.connect(config.DATABASE_SQLITE3)

    def _run(self, driver):

        driver.get("https://app.wonderland.money/#/mints")

        # wait for page load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".choose-bond-view-card"))
        )

        mints = driver.find_elements(
            By.CSS_SELECTOR, ".bond-table-btn"
        )

        # TODO


runner = TimeAutoClaim()
runner.run()
