from utils.paths import PATHS

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import asyncio
from urllib.parse import unquote
import random


class TrendUp:
    def trend_up(self, hashtag: str, likes_retweets: int, tab= "Latest" ):
        return asyncio.run(trend_up(self,hashtag,likes_retweets,tab))






#retweet and like tweets that contains certain hashtag
async def trend_up(self, hashtag: str, likes_retweets: int, tab= "Latest" ,recursion_count=0):
    #return visible 'like buttons' in our scope
    async def like_btns():
        return self.get_element(EC.visibility_of_all_elements_located((By.XPATH,PATHS["LikeButton"])),10)
    
    #return visible 'retweet buttons' in our scope
    async def retweet_btns():
        return self.get_element(EC.visibility_of_all_elements_located((By.XPATH,PATHS["RetweetButton"])),5)
    
    #return search tab if it's visible
    async def search_tab(tab):
        return self.get_element(EC.visibility_of_element_located((By.XPATH,PATHS[tab])),5)
    
    #check the current tab
    async def current_tab(locals):
        for tmp in ["top","latest","photos","videos"]:
            Tab = await locals[f"{tmp}_tab"]
            if eval(Tab.get_attribute("aria-selected").capitalize()) == True:
                return tmp
    
    #take tab_name as input and then click on the tab that has the name
    move_to_tab = lambda tab : self.actions.move_to_element(locals()[f"{tab.lower()}_tab"]).\
        pause(random.uniform(0.7,1.1)).click().pause(random.uniform(0.5,0.8)).perform()
        
    
    #cancel all tasks except self.trend_up
    cancel_all_tasks = lambda: [task.cancel() for task in list(asyncio.tasks.all_tasks())[:1]]
    
    
    #create tasks for like and retweet butttons
    like_btns = asyncio.create_task(like_btns())
    retweet_btns = asyncio.create_task(retweet_btns())

    #create task for taba
    for tmp in ["top","latest","photos","videos"]:
        locals()[f"{tmp}_tab"] = asyncio.create_task(search_tab(f"Search({tmp.capitalize()})"))
    
    
    #in case there is too much recursion
    if recursion_count >= 20:
        cancel_all_tasks()
        raise Exception(f"could not perform {likes_retweets} likes and retweets")
    
    #in case requested tweets are too much
    if int(likes_retweets) > 50:
        cancel_all_tasks()
        raise Exception("too much retweets and likes")
    
    
    #in case selected tab does not exist
    if (tab := tab.lower().strip()) not in ["top","latest","photos","videos"]:
        cancel_all_tasks()
        raise Exception("Tab Must Be one of (Top,Latest,Photos,Videos)")
    
    
    #in case we're not on the hashtag page
    if hashtag not in unquote(self.driver.current_url):
        #redirect to the hashtag page
        cancel_all_tasks()
        self.search(hashtag)
        return await trend_up(self,hashtag,likes_retweets,recursion_count= recursion_count + 1,tab=tab)
    
    
    #move to the requested tab
    for tmp in ["top","latest","photos","videos"]:
        if tab == tmp:
            requested_tab = await locals()[f"{tmp}_tab"]
            #in case we're not on the requested tab
            if eval(requested_tab.get_attribute("aria-selected").capitalize()) == False:
                self.actions.move_to_element(requested_tab).pause(random.uniform(0.7,1.1)).click().pause(random.uniform(0.5,0.8)).perform()
        
    
    #wait for tasks to finnish
    like_btns = await like_btns 
    retweet_btns = await retweet_btns
    
    #in case we liked or retweeted all tweets in our scope move
    if like_btns == None or retweet_btns == None:
        #scroll down to find more tweets
        self.driver.execute_script("window.scrollBy(0, 5000);")
        return await trend_up(self,hashtag,likes_retweets,recursion_count= recursion_count + 1,tab=tab)
    
    #loop through the list of like and retweet buttons and click them
    tmp = 0   
    for tmp,(like_btn,retweet_btn) in enumerate(zip(like_btns,retweet_btns)):
        #in case we accidentally changed the tab
        if await asyncio.create_task(current_tab(locals())) != tab:
            move_to_tab(tab)
            break

        try:
            self.actions.move_to_element(like_btn).pause(random.uniform(0.7,1.1)).click().pause(random.uniform(0.5,0.8)).perform()
            self.actions.move_to_element(retweet_btn).pause(random.uniform(0.5,0.8)).click().pause(random.uniform(0.9,1.4)).perform()
            
            #in case confirm retweet in not visible
            if (confirm_retweet := self.get_element(EC.visibility_of_element_located((By.XPATH,PATHS["RetweetConfirm"])),10)) is None:
                print("Confirm Retweet Button is not visible")
                break
        
            self.actions.move_to_element(confirm_retweet).pause(random.uniform(0.8,1.3)).click().pause(random.uniform(0.5,1.1)).perform()

        #in case the there is an error break the loop      
        except StaleElementReferenceException:
            break


    #in case the requested likes and retweets is more than the what we liked and retweeted
    if likes_retweets > tmp:
        return await trend_up(self,hashtag,  likes_retweets - tmp,   recursion_count= recursion_count,tab=tab)
    return self