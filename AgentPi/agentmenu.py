from getpass import getpass
from agentsocket import SocketAccess
from location import getLocation2


class Menu:
    
    """
        Main menu for Agent Pi:
        designed to allow user to unlock and return the car the pi is based on.
        Initilialised by passing based cars registration.
    """
    def __init__(self,car):
        try:
            from facialRecog import facialRecog
            self.facialRecognitionInstalled = True
        except:
            self.facialRecognitionInstalled = False

        #agentpi represents current car (rego)
        self.running = True
        self.unlocked = False
        self.carRego = car
        
    
    def start(self):
        """
            starts running UI.
            creates running loop allowing user input to a multiple choice list.
            Either Return/unlock car depending on state and quit.
        """
        self.running = True
        self.unlocked = False
        self.printMenu()
        while(self.running):
            #get user input
            try:
                choice = int(input("\n> "))
            except ValueError:
                print("Please enter number within menu options")
            else:
                if choice > 2 or choice <= 0:
                    print("Please enter number within menu options")
                else:
                    if choice == 2:
                        self.running = False
                        print("Thank you")
                    elif choice == 1:
                        if self.unlocked:
                            self.returnCar()
                        else:
                            self.unlockCar()


    def returnCar(self):
        """
            Returns car by creating new socket object and sending
            car rego to the Master Pi
        """
        print("car returned.")
        newSocket = SocketAccess()
        if(newSocket.returnCar(self.carRego)):
            #lock car and send data to masterpi
            self.unlocked = False
            print("Thank you for driving with us!\n")

        self.printMenu()

    def unlockCar(self):
        """
            sub menu to unlock car by logging in.
            Allows user to choose logging in with username and password or facial recognition.
            login is verified by sending credentials to master pi and receiving true/false from socket.
            Once logged in, state of car will be unlocked.
            Also allows user to return to previous menu.
        """
        testing = True

        print("Login: ")
        print("1. Username/Password")
        print("2. Facial Recognition")
        print("3. Quit")

        
        try:
            choice = int(input("\n> "))
        except ValueError:
            print("Please enter number within menu options")
        else:
            if choice > 3 or choice <=0:
                print("Please enter number within menu options")
            else:
                #login with username/password
                if choice == 1:
                    username = input("Enter Username: ").lower()
                    password = getpass("Enter Password: ")
                    newSocket = SocketAccess()
                    self.unlocked = newSocket.loginCheck(username,password,self.carRego)
                    if self.unlocked == False:
                        print("""Either Username and Password do not match server database\n
                                Connection could not be made\n
                                or booking was not made for todays date.""")
                    if self.unlocked == True:
                        #Send location to the Master Pi here
                        location = getLocation2()
                        newSocket.sendLocation(self.carRego, location)

                elif choice == 2:
                    #login with facial recognition
                    if self.facialRecognitionInstalled:
                        print("getting facial scan..")
                        #do scan
                        facialRecog.facial_login(self)
                        print("accepted. Car unlocked..")
                        self.unlocked = True
                    else:
                        print("Facial recognition not installed")
                    
                    #DO face check

                    if self.unlocked == True:
                        #Send location to the Master Pi
                        location = getLocation2()
                        newSocket.sendLocation(self.carRego, location)

                elif choice == 3:
                    print("Quit")

        if self.unlocked:
            print("Car unlocked.")
        self.printMenu()
        #To Do
        
        
    def printMenu(self):
        """
           Frenquently used menu list to print options to user. 
        """
        print("\n\nMenu: \n")
        if self.unlocked:
            print("1. Return car")
        else:
            print("1. Unlock car")
        print("2. Quit")