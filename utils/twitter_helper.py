from selenium.common.exceptions import TimeoutException,StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import random
from time import sleep
import time
import json


from utils.paths import PATHS
from utils.signin import Signin
from accounts.accounts_manager import AccountsManager

class TwitterHelper(Signin):
    def get_element(self, condition, time):
        try:
            Element = WebDriverWait(self.driver,time).until(
                condition
            )
        
        except TimeoutException:
            return None
        
        else:
            return Element

    #check if certain keywords are in the page for a certain duration in seconds
    def check_words(self, keywords : list, duration : int):
        Body = self.get_element(EC.visibility_of_element_located((By.XPATH,PATHS["Body"])),5)
        
        start_time = time.time()
        time_spent = 0
        
        #keep running as long as time spent in the loop less than the required checking duration 
        while time_spent < duration:
            current_text = Body.text.lower().strip()
            print(current_text)

            #in case there is at least one of these words return true
            if any([True for word in keywords if word in current_text]) == True:
                return True
            #update time spent
            time_spent = time.time() - start_time
        
        return False


    def _is_loaded(self):
        #in case body is not present after 20 seconds raise Exception
        if self.get_element(EC.presence_of_element_located((By.XPATH,PATHS["Body"])),20) is None:
            raise Exception("Page is not loading")
    
   
    def _type(self,location : object ,txt : str):
        #check if placeholder is clickable else return None
        if(Placeholder := self.get_element(EC.element_to_be_clickable(location),100)) is None:
            return
        
        #hover over the placeholder for some time then click
        self.actions.move_to_element(Placeholder).pause(random.uniform(0.5,1.3)).perform()
        Placeholder.click()
        
        #type the text
        sleep(random.uniform(0.7,1.2))
        Placeholder.send_keys(txt)

        return Placeholder
        
    #add cookies to the browser
    def add_cookies(self):
        #load cookies from the database
        with AccountsManager() as AccountManager:
            if (cookies := AccountManager.cur.execute("SELECT cookie FROM cookies WHERE user_id = ? ",(self.id,)).fetchone())[0] is None:
                #in case there is no cookies
                print("There is no cookies available")
                return
            
            #decerialize cookies json object
            cookies = json.loads(cookies[0])

            #loop through cookies json object
            for cookie in cookies:
                #in case expiration date is a float
                if(isinstance(cookie.get('expiry'), float)):
                    cookie["expiry"] = int(cookie["expiry"])

                #add cookie
                self.driver.add_cookie(cookie)

    
    #tweet using the tweet box in the home page
    def _tweet_from_home(self, txt: str,recursion_count = 0): 
        if recursion_count == 5:
            raise Exception("can't click the tweet box on homepage")
        
        #get compose tweet box and tweet button
        if (compose_tweet := self.get_element(EC.visibility_of_element_located((By.XPATH,PATHS["ComposeTweet(Home)"])),10)) is None:
            raise Exception("compose tweet box is not present in home page")
       
        if (tweet := self.get_element(EC.visibility_of_element_located((By.XPATH,PATHS["Tweet(Home)"])),10)) is None:
                   raise Exception("tweet button is not present in home page")
        
        try:
            #hover over the placeholder for some time then click and clear and type text
            self.actions.move_to_element(compose_tweet).pause(random.uniform(0.5,1.3)).perform()
            compose_tweet.click()
            compose_tweet.send_keys(txt)
            
            #hover over the button for some time then click
            self.actions.move_to_element(tweet).pause(random.uniform(0.5,1.3)).perform()
            self.driver.execute_script("window.scrollTo(0, 0);")
            tweet.click()
            
        
        except StaleElementReferenceException:
            #in case there is an error repeate the process
            self._tweet_from_home(txt,recursion_count = recursion_count + 1)        
        

    def _tweet_from_compose_box(self, txt: str):
        #get tweet button on the left
        if (compose_tweet := self.get_element(EC.element_to_be_clickable((By.XPATH,PATHS["ComposeTweet"])),15)) is None:
            raise Exception("Compose Tweet Button is not clickable. Please navigate to home page")

        #hover over the compose tweet for some time then type the click
        self.actions.move_to_element(compose_tweet).pause(random.uniform(0.5,1.3)).click().perform()

        if (placeholder := self.get_element(EC.presence_of_element_located((By.XPATH,PATHS["Type(ComposeBox)"])),120)) is None:
            raise Exception("Type tweet in the compose tweet box is not visible")
        
        self.actions.move_to_element(placeholder).pause(random.uniform(0.5,1.3)).click().pause(random.uniform(0.7,1.4)).send_keys(txt).perform()

        #check if tweet button is visible the tweet button
        if (tweet := self.get_element(EC.presence_of_element_located((By.XPATH,PATHS["Tweet(ComposeBox)"])),50)) is None:
            raise Exception("Tweet Button in the compose tweet box is not visible")
        
        #hover over the next button for some time then type the click
        self.actions.move_to_element(tweet).pause(random.uniform(0.5,1.3)).perform()
        tweet.click()