import mastermenu
from databaseaccess import DatabaseUtils
from mastersocket import MasterSocket
from passlib.hash import sha256_crypt
from getpass import getpass
import threading
import sys
import re

class LoginMenu:
    """
        initial menu for Master Pi.
        Allows user to login.
        File to run. begins threads for a UI and for the socket
    """


    def start(self):
        """
            initialises database if not already created.
            runs ui for user
        """

        with DatabaseUtils() as db:
            db.createDatabase()
            #initialise database
        print("\nWelcome")
        running = True
        self.printMenu()
        while running: 
            try:    #get user input
                choice = int(input("> "))
            except ValueError:
                print("Please enter number within menu options")
            else:
                if choice > 3 or choice <= 0:
                    print("Please enter number within menu options")
                else:
                    if choice == 1:
                        self.register()
                    elif choice == 2:
                        self.login()
                    elif choice == 3:
                        running = False
                        print("\nThank you")


    def login(self):
        """
            prompts user for their username and password
            checks off credentials with database.
            If correct, enters master menu.
        """
        currentUser = input("Enter Username: ").lower()
        #Use getpass as it hides the input of the password in console
        password = getpass()
        found = False
        with DatabaseUtils() as db:
            userList = db.getUsers()
            for user in userList:
                #check user exists and verify password with encryption
                if user[0] == currentUser and sha256_crypt.verify(password,user[1]):
                    if user[2] == "CUSTOMER":
                        userMenu = mastermenu.CustomerMenu()
                    elif user[2] == "ADMIN" or user[2] == "MANAGER" or user[2] == "ENGINEER":
                        userMenu = mastermenu.AdminMenu()
                    
                    userMenu.start(currentUser)
                    found = True
            if not found:
                print("Incorrect username or password")

        print("\nReturning to login..\n")
        self.printMenu()

    def register(self):
        """
            allows user to create a new account given username, email and password.
            Inserts data into database after validation
        """
        print("(below choice only for testing. removed once admin accounts are accessible)")
        print("1. Customer")
        print("2. Admin")
        print("3. Manager")
        print("4. Engineer\n")
        userType = ""
        while True:
            try:    #get user input
                choice = int(input("> "))
            except ValueError:
                print("Please enter number within user options")
            else:
                if choice > 4 or choice <= 0:
                    print("Please enter number within user options")
                else:
                    if choice == 1:
                        userType = "CUSTOMER"
                        break
                    elif choice == 2:
                        userType = "ADMIN"
                        break
                    elif choice == 3:
                        userType = "MANAGER"
                        break
                    elif choice == 4:
                        userType = "ENGINEER"
                        break
        
        newUser = input("Enter new username: ").lower()
        while True:
            email = input("Enter your email address: ")
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if re.search(regex,email):
                break
            else:
                print("Invalid email. Retry:")
        #Asks user to confirm the password entry to validate input
        valid = False
        while (valid == False):
            newPassword = getpass(prompt='Enter a password: ')
            confirmPassword = getpass(prompt='Confirm Password: ')
            #verify new password is correct
            if (newPassword == confirmPassword and len(newPassword)>0):
                valid = True
            else:
                print("Invalid password, please try again")
        
        with DatabaseUtils() as db:
            userList = db.getUsers()
            for user in userList:
                if user[0] == newUser:
                    valid = False
                    print("Sorry, username already exists")
                    #check user doesnt already exist then insert if not
            if valid:
                db.insertUser(newUser,email,sha256_crypt.hash(newPassword),userType)
                print("\nuser created\n")
                
        print("\nReturning to login..\n")
        self.printMenu()

    def printMenu(self):
        """
            general menu function to allow easier reprints
        """
        
        print("\n1. Register new user")
        print("2. Login as user")
        print("3. Quit\n")


## Main ##
##start UI and Socket on seperate threads ##
def startUI():
    """
        class to start first thread: UI
    """
    newProgram = LoginMenu()
    newProgram.start()

def startSocket():
    """
        class to start second thread: socket
    """
    socket = MasterSocket()
    socket.start()

#Thread two streams: ui and socket listening

threads = []
ui = threading.Thread(target=startUI)
socketListener = threading.Thread(target=startSocket)

threads.append(ui)
threads.append(socketListener)
socketListener.daemon = True

for thread in threads:
    thread.start()
    #start program
while True:
    
    if not ui.is_alive():
        #if UI quits, prompt to end socket
        sys.exit()
        break
        

