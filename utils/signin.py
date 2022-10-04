from utils.paths import PATHS

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import random
from time import sleep

class Signin:
    def signin(self):
        #check if signin button is present
        if (signin_btn := self.get_element(EC.element_to_be_clickable((By.XPATH,PATHS["SigninBtn"])),10)) is None:
            raise Exception("Signin button is not clickable")
        
        #hover over and click the signin button
        self.actions.move_to_element(signin_btn).pause(random.uniform(0.5,1.2)).click().perform()
        
        #check if the signin modal is displayed
        if self.__signin_modal() is False: 
            raise Exception("Sign in modal is not displayed")

        
        self.__type("Email")

        #in case email is invalid
        if self.__check_errors() is True: raise Exception("Email is invalid")

        #in case twitter is suspecting unusual activity
        if self.__check_issues() is True:
            self.__type("Username")
            if self.__check_errors() is True:
                raise Exception("Username is invalid")
        
        #type password
        self.__type("Password")

        if self.__check_errors() is True: 
            raise Exception("Password is invalid")

    
    #return true if signin modal is displayed
    def __signin_modal(self):
        if self.get_element(EC.visibility_of_element_located((By.XPATH,PATHS["SigninModal"])),100):
            return True
        return False
    

    #this function is intended to type the email, username or password
    def __type(self,target):
        #this function is intended to click the "reveal your password" button
        def reveal_pass():
            if (reveal_pass := self.get_element(EC.element_to_be_clickable((By.XPATH,PATHS["RevealPass"])),5)) is None:
                raise Exception("Reveal Password Button is not clickable")

            #hover over the next button for some time then type the click
            self.actions.move_to_element(reveal_pass).pause(random.uniform(0.5,1.3)).click().perform()



        #in case of unexpected input
        if target not in ["Email","Username","Password"]:
            raise Exception("invalid target")

        #type the target text in the target placeholder if clickable, else raise exception
        #print(getattr(self,target))
        if (placeholder := self._type(  (By.XPATH,PATHS[target])  ,  getattr(self,target))  ) is None:
            raise Exception(f"{target} placeholder is not clickable")
        
        
        #Occasionally click the reveal password button when typing the email
        if target == "Password" and random.randint(0,99) < 50:
            reveal_pass()

        #submit placeholder
        sleep(random.uniform(0.7,1.3))
        self.__submit(placeholder,(By.XPATH,PATHS[f"Next({target})"]))

    def __submit(self,placeholder,nxt_location):
        #50% of the time submit directly
        if random.randint(0,99) < 500:
            placeholder.send_keys(Keys.RETURN)
            return
        

        #sometimes click the Next button to submit email
        if (Next := self.get_element(EC.visibility_of_element_located(nxt_location),10)) is None :
            raise Exception("Next Button is not visible")

        #hover over the next button for some time then type the click
        self.actions.move_to_element(Next).pause(random.uniform(0.5,1.3)).click().perform()



    #check if twitter is suspecting some unusual activities
    def __check_issues(self):
        if (Modal := self.get_element(EC.visibility_of_element_located((By.XPATH,PATHS["SigninModal"])),10)) is None:
            raise Exception("Signin Modal is not present")
        
        #return True if any of the following words are in the text else false
        return any([True for word in ["verify","unusual","activity"]if word in Modal.text.lower()])

    def __check_errors(self):
        Body = self.get_element(EC.visibility_of_element_located((By.XPATH,PATHS["Body"])),5)
        sleep(1.5)

        #return True if any of the following words are in the text else false
        return any([True for word in ["sorry","could not","wrong password","incorrect","try again"]if word in Body.text.lower()])   