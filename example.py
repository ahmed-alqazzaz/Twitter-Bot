from accounts.accounts_manager import AccountsManager
from twitter_bot import TwitterBot
from time import sleep
import random

#The account should be added only once
with AccountsManager() as Manager:
    #add account to accounts.db

    #you should replace the following with your account credentials
    email = "account's email@gmail.com"
    username = "account's username"
    password = "XXXXXXXXXXXXXXXXXXXXX"
    #Manager.add_account(email= email,username=username,password=password)

with AccountsManager() as Manager:
    #provide one of the account credentials to receive the rest
    id,username,email,password = Manager.account_info("email",email)


#login to twitter using the credentials from the database
with TwitterBot(id=id,Username=username,Email=email,Password=password) as bot:
    #get trends
    print(bot.trends())
    
    """
      like and retweet tweets that contain specific hashtag or topic
    """
    bot.trend_up(hashtag = "#Tesla",likes_retweets= 2,tab = "Latest")
    
    sleep(random.uniform(1.4,3.7))
    
    #return back to pevious page
    bot.driver.back()
    #tweet from home page
    for i in range(5):
        sleep((random.uniform(1.2,3.1)))
        bot.tweet(f"Hello World{i}")
    
    #naviage to certain topic or twitter account
    bot.search("Elon Musk")
    #tweet from hashtag or topic page
    bot.search("#Hashtag")
    for i in range(5):
        sleep((random.uniform(1.2,3.1)))
        bot.tweet(f"Hello World{i}")