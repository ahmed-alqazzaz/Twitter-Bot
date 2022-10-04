from utils.paths import PATHS
from features.trend_up import TrendUp

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import random

class Features(TrendUp):
     #tweet from the main page
    def tweet(self,txt: str):
        #in case we are in the home page
        if self.driver.current_url == "https://twitter.com/home":
            self._tweet_from_home(txt)
            return self
        #in case we're not
        self._tweet_from_compose_box(txt)
        return self
    
    
    #return a list of current trends
    def trends(self,return_element=False):
        if (trends := self.get_element(EC.visibility_of_all_elements_located((By.XPATH,PATHS["Trends"])),50)) is None :
            raise Exception("can't find trends")
        
        if return_element == True:
            return [trend for trend in trends]

        #return a list of trends
        return [trend.text.split("\n")[1] for trend in trends]

    
    
    #search for a certain topic 
    def search(self, txt: str):
        #define a lambda function that raises StopIteration
        stopiteration = lambda : exec("raise StopIteration")
        
        try:
            #in case the text is in the trends, click it directly
            [self.actions.move_to_element(trend).pause(random.uniform(0.5,1.3)).click().perform() and stopiteration()\
                for trend in self.trends(True) if trend.text.split("\n")[1] == txt]

        #this error will be raised once suggestion is clicked
        except StaleElementReferenceException: 
            return self
        
        
        #in case we did not find the text in the trends
        if (search_bar := self.get_element(EC.visibility_of_element_located((By.XPATH,PATHS["SearchBar"])),5)) is None :
            raise Exception("can't find search bar")
        
        
        #hover over the placeholder for some time then click and clear and type text
        self.actions.move_to_element(search_bar).pause(random.uniform(0.5,1.3)).double_click()\
            .pause(random.uniform(0.3,0.6)).click_and_hold().send_keys(Keys.CLEAR).pause(random.uniform(0.8,1.3)).send_keys(txt).perform()
         
        
        #in case suggestion list pops up within 3 seconds
        if (suggestionlist := self.get_element(EC.visibility_of_all_elements_located((By.XPATH,PATHS["SuggestionList"])),3)):
            try:
                #click the suggestion if the topic we're searching for is in the suggestions
                [self.actions.move_to_element(suggestion).pause(random.uniform(0.5,1.3)).click().perform() and stopiteration()\
                for suggestion in suggestionlist if suggestion.text.split("\n")[0] == txt]
            
            #this error will be raised once suggestion is clicked
            except StaleElementReferenceException: 
                return self
        
        #in case suggestion does not match the topic, so we search directly for it
        search_bar.send_keys(Keys.RETURN)
        return self