from utils.twitter_helper import TwitterHelper
from utils.paths import PATHS
from features.features import Features
from accounts.accounts_manager import AccountsManager

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from dotenv import load_dotenv
import os
from time import sleep
import random


#this class is intended to only be used as a context manager(used with 'with' statement)
class TwitterBot(TwitterHelper,Features):
    def __init__(self,id,Email,Username,Password):
        self.__is_context_manager = False
        self.id = id
        self.Email = Email
        self.Username = Username
        self.Password = Password
    
    def __getattribute__(self, name):
        #in case the class has'nt been accessed as context manager
        if object.__getattribute__(self, "_TwitterBot__is_context_manager") == False:
            raise Exception("this class in intended to only be used as context manager")

        return object.__getattribute__(self, name)


    def __enter__(self):
        #in case the class was used as context manager
        self.__is_context_manager = True

        #set up chromedriver options C:\Users\acer\AppData\Local\Google\Chrome\User Data\Default
        option = webdriver.ChromeOptions()
        prefs = {"credentials_enable_service": False,
        "profile.password_manager_enabled": False}
        option.add_experimental_option("prefs",prefs)
        option.add_experimental_option("excludeSwitches",["enable-automation"])
        option.add_experimental_option("useAutomationExtension","False")
        option.add_argument('--disable-blink-features=AutomationControlled')
        
        #export environment variable
        load_dotenv()
        PATH = rf"{os.getenv('CHROMEDRIVER_PATH')}"

        #instantiate chrome driver
        self.driver = webdriver.Chrome(executable_path = PATH,options = option)
        self.driver.delete_all_cookies()
        self.driver.maximize_window()
        self.actions = ActionChains(self.driver)
        
        #go to twitter
        self.driver.get("https://twitter.com")
        
        #add the cookies and refresh
        self.add_cookies()
        sleep(random.uniform(1.9,2.5))
        self.driver.refresh()

        #in case we're not logged in
        if self.login_status() == False:
            self.signin()
            sleep(4)

        return self
        

    def __exit__(self, exc_type, exc_val, exc_tb):
        #add cookies to the database
        sleep(random.uniform(3.5,3.8))
        with AccountsManager() as Manager:
            Manager.save_cookies(self.driver.get_cookies(),self.id)

        self.driver.quit()
        

    #return True in case we're logged in
    def login_status(self):
        #check if page is loaded 
        self._is_loaded()
        
        #return True if url matches
        try:
            #if we are on home page, this means we're logged in
            WebDriverWait(self.driver,3).until(
                EC.url_to_be('https://twitter.com/home')
            )
        #in case there is errors, this means url did not match
        except TimeoutException:
            return False
        
        #in case there is no exceptions
        return True