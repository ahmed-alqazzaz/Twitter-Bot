import sqlite3
import json
import pathlib

#this class is intended to only accessed using the with statement
class AccountsManager:
    globals()["is_context_manager"] = False

    def __getattribute__(self, name):
        #in case the class has'nt been accessed as context manager
        if globals()["is_context_manager"] == False:
            raise Exception("this class in intended to only be used as context manager")

        return object.__getattribute__(self, name)

    def __enter__(self):
        globals()["is_context_manager"] = True
        #connect to the database
        self.con = sqlite3.connect(fr"{pathlib.Path(__file__).parent.resolve()}\accounts.db")
        self.cur = self.con.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        #commit changes
        self.con.commit()
        self.con.close()


    #get account information that corresponds to  one of id/email/username
    def account_info(self, column: str,value: str):
        #check if the provided column is accurate
        if column not in ["id","email","username"]:
            raise Exception("You should provide one of id/email/username")
            
        #return account information
        return self.cur.execute(f"SELECT * FROM users WHERE {column}=(?) ",(value,)).fetchone()
    


    #add account to accounts.db
    def add_account(self, email: str, username: str, password: str,phone = None,cookie=None):
        #add the account to the database
        try:
           self.cur.execute("INSERT INTO users(username,password,email) VALUES(?,?,?)",(username,password,email))    
        #in case one of email or username is already in the database integrity error will be raised
        except sqlite3.IntegrityError:
            raise Exception("Account Already Exists")

        #get id of the added row
        id = self.cur.lastrowid
        
        #add phone number
        try:
           self.cur.execute("INSERT INTO phones(user_id,phone) VALUES(?,?)",(id,phone))
        except sqlite3.IntegrityError:
            raise Exception("Phone number is linked to another account")
        
        #add cookies
        self.cur.execute("INSERT INTO cookies(user_id,cookie) VALUES(?,?)",(id,cookie))

    
    #update at least one of username,email,password,phone,cookie depending on the given id
    def update_account(self, id: int, username = None, email = None, password = None, phone = None, cookie = None):
        #in case all the following is none
        if not any((username,email,password,phone,cookie)):
            raise Exception("you must at least change one of email/username/password/phone number/cookie")

        
        #check if any of the following should be updated
        for tmp in (username,email,password):
            #in case tmp is not None
            if tmp:
                self.cur.execute("UPDATE users SET email = ? WHERE id = ?",(tmp,id))
        
        #in case phone is not None   
        if phone:
            self.cur.execute("UPDATE phones SET phone = ? WHERE id = ?",(phone,id))
        
        #in case cookie is not None 
        if cookie:
            self.cur.execute("UPDATE cookies SET cookie = ? WHERE id = ?",(cookie,id))

    
    def save_cookies(self, cookies: str, id: int):
        #convert cookies to json string
        cookies = json.dumps(cookies)
        
        # get a list of tuples of ids from the database
        ids = self.cur.execute("SELECT user_id FROM cookies").fetchall()
    
        #in case id is in the database
        if id in [id[0] for id in ids]:
            self.cur.execute("UPDATE cookies SET cookie = ? WHERE user_id=?",(cookies,id))
        
        else:
            self.cur.execute("INSERT INTO cookies(user_id,cookie) VALUES(?,?)",(id,cookies))