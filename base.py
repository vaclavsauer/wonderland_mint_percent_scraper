#!/usr/bin/python
# -*- coding: UTF-8 -*-


import datetime
import logging
import os
import time
from distutils.dir_util import copy_tree

from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

import config


class SessionRemote(webdriver.Remote):
    def start_session(self, desired_capabilities, browser_profile=None):
        # Skip the NEW_SESSION command issued by the original driver
        # and set only some required attributes
        self.w3c = True


class WanderBase(object):
    COUNTDOWN = 5  # seconds

    SKIP_WAIT = False
    # SKIP_WAIT = True

    SAVE_TO_DB = True
    # SAVE_TO_DB = False

    RUN_ATTEMPTS = 3

    def run(self):
        print("❤️ {} welcomes you ❤️".format(self.__class__.__name__))

        # Select firefox profile to start with
        # by using existing copy of firefox profile or by creating new copy of firefox profile
        available_profiles = [
            p
            for p in os.listdir(config.FIREFOX_PROFILES_DIR)
            if config.FIREFOX_PROFILE in p and len(p) > len(config.FIREFOX_PROFILE)
        ]

        selected_profile = None
        for profile in available_profiles:
            if "cookies.sqlite-shm" not in os.listdir(os.path.join(config.FIREFOX_PROFILES_DIR, profile)):
                print("Using existing profile dir {}️".format(profile))
                selected_profile = profile
                break

        if not selected_profile:
            for i in range(0, config.MAX_FIREFOX_PROFILES):
                selected_profile = "{}.{}".format(config.FIREFOX_PROFILE, str(i))
                if selected_profile not in available_profiles:
                    print("Creating new profile dir {}️".format(selected_profile))
                    break

            copy_tree(
                os.path.join(config.FIREFOX_PROFILES_DIR, config.FIREFOX_PROFILE)
                      ,
                os.path.join(config.FIREFOX_PROFILES_DIR, selected_profile)
            )

        print("Starting Firefox 🦊️")
        options = FirefoxOptions()
        options.add_argument("-profile")
        options.add_argument(os.path.join(config.FIREFOX_PROFILES_DIR, selected_profile))
        driver = Firefox(options=options)

        # log in to metamask
        print("Initializing Metamask 🦊")
        driver.get(config.METAMASK_EXTENSION_URL)
        WebDriverWait(driver, 30).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#password"))
        )
        driver.find_element(By.CSS_SELECTOR, "#password").send_keys(config.METAMASK_PWD)
        driver.find_element(By.CSS_SELECTOR, "button").click()
        WebDriverWait(driver, 30).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".wallet-overview"))
        )

        print("Done")

        # Wait until whole minute
        self.countdown(5)

        # Main loop
        try:
            while True:

                # Fix having minimized window, where we can't get prices
                if driver.get_window_position()["x"] < 0:
                    driver.maximize_window()

                for attempt in range(0, self.RUN_ATTEMPTS):
                    try:
                        self._run(driver)
                        break
                    except Exception:
                        logging.exception("\t❗ ️️UPS ❗️️ 🙃")
                        print(f"ℹ️️attempt #{attempt + 2}...")

                time.sleep(
                    60.0
                    - datetime.datetime.utcnow().second
                    - datetime.datetime.utcnow().microsecond / 1000000
                )
        except Exception as e:
            logging.exception("")
        finally:
            driver.quit()
            driver.close()

    def countdown(self, countdown_seconds):
        if self.SKIP_WAIT:
            return

        sleep_seconds = self.get_sleep()

        print(f"⏳ Starting in {sleep_seconds:.1f} seconds...")

        if sleep_seconds > countdown_seconds:
            time.sleep(sleep_seconds - countdown_seconds)
        else:
            time.sleep(sleep_seconds % 1)

        sleep_seconds = self.get_sleep()
        while sleep_seconds > 1:
            print(f"⏳  {int(sleep_seconds) + 1}")
            time.sleep(sleep_seconds % 1)
            sleep_seconds = self.get_sleep()

        print(f"⏳  {int(sleep_seconds) + 1}")
        time.sleep(sleep_seconds % 1)
        print("Working... 💸💵💸")

    @staticmethod
    def get_sleep():
        now = datetime.datetime.utcnow()
        return 60.0 - now.second - now.microsecond / 1000000

    def _run(self, driver):
        raise NotImplementedError()


# --- NOT WORKING

# -----------------------------------
# --- does not open profile

# from selenium import webdriver
# profile = webdriver.FirefoxProfile(r"C:\Users\vasek\AppData\Roaming\Mozilla\Firefox\Profiles\ppz4ebfh.selenium")
# driver = webdriver.Firefox(profile)
# driver.get("https://www.example.com/membersarea")

# -----------------------------------
# --- does not allow opening of new window

# options = FirefoxOptions()
# options.add_argument("-profile")
# options.add_argument(r"C:\Users\vasek\AppData\Roaming\Mozilla\Firefox\Profiles\ppz4ebfh.selenium")
# options.add_argument("-no-remote")
# driver = Firefox(options=options)

# -----------------------------------
# --- does connect to existing driver, but we can not control two windows

# store current driver session_id and url
# with open("session", "w") as f:
#     f.write(
#         json.dumps(
#             {
#                 "session_id": driver.session_id,
#                 "url": driver.command_executor._url,
#             }
#         )
#     )
# # open session by session_id and url
# with open("session", "r") as f:
#     session = json.loads(f.read())
# driver2 = SessionRemote(
#     command_executor=session["url"], desired_capabilities={}
# )
# driver2.session_id = session["session_id"]
# driver2.start_session(desired_capabilities={})

# -----------------------------------

# -----------------------------------
# --- random stuff
# options.set_headless()

# open new tab
# driver.execute_script("window.open('');")

# switch tab
# driver.switch_to.window('e3d38318-d191-4d75-b3a5-be4eb7d30d4f')
# -----------------------------------
