from databaseaccess import DatabaseUtils
from calendaraccess import CalendarUtils
from pushbullet_access import PushbulletAccess
from passlib.hash import sha256_crypt
import re
import datetime
import requests
from datetime import date

class CustomerMenu:
    """
        Main menu for logged in user.
        Requires username to personalise the UI
    """
    
    def start(self,user):
        #cleans terminal for new menu
        print(chr(27) + "[2J")
        running = True
        print("\nWelcome "+user+"\n")
        self.printMenu()
        self.user = user
        #start menu display and assure database is up to date
        with DatabaseUtils() as db:
            self.cars = db.getAllCars()
            if not self.cars:
                db.populateDatabase()
                self.cars = db.getAllCars()

        while(running):
            try:
                choice = int(input("> "))
            except ValueError:
                print("Please enter number within menu options")
            else:
                if choice > 6 or choice <= 0:
                    print("Please enter number within menu options")
                else:   #get user input
                    if choice == 1:
                        self.bookingHistory(user)
                    elif choice == 2:
                        self.showCars()
                    elif choice == 3:
                        self.searchCars()
                    elif choice == 4:
                        self.bookCar()
                    elif choice == 5:
                        self.cancelBooking()
                    elif choice == 6:
                        running = False
                        print("Thank you")
                    

    def printMenu(self):
        """
            generic print statement for menu.
            function reused throughout class
        """
        print("\nMenu:\n")
        print("1. View Booking History")
        print("2. Show available cars")
        print("3. Search for cars")
        print("4. Book Car")
        print("5. Cancel booking")
        print("6. Logout\n")

    def bookingHistory(self, user):
        """
            prints booking history for given user
            in format:
            Booking id      Rego     StartDate    EndDate
        """
        print("Booking History for " + user + ": ")
        #connect to database and get booking history for user
        with DatabaseUtils() as db:
            self.bookings = db.getBookingHistory(user)
        
        data = ["Booking ID", "Rego", "Start Date", "Finish Date"]
        row_format ="{:<17}"*(len(data))
        print(row_format.format(*data))
        for bookings in self.bookings:
            print(row_format.format(str(bookings[0]),bookings[1],str(bookings[2]),str(bookings[3])))
        self.printMenu()
        

    def showCars(self):
        """
            shows all available cars given todays date isnt booked for that car
            in format:
            Rego     Model    Body    Seats    Colour     Price Per Day      Location     Returned (y/n)
        """
        print("Cars Currently Available: \n")
        #connect to database and get all available cars given date
        with DatabaseUtils() as db:
            today = datetime.date.today()
            availableCars = db.getAvailableCars(today.strftime("%d-%m-%Y"))
        
            data = ["Rego","Model","Body","Seats","Colour","Price Per Day($)","Location"]        
            row_format ="{:<17}"*(len(data))
            print(row_format.format(*data))
            for car in availableCars:
                print(row_format.format(car[0],car[1],str(car[2]),str(car[3]),str(car[4]),str(car[5]),str(car[6]))) 
                
        self.printMenu()

    def searchCars(self):
        """
            prompts user to search for specific car given attribute type:
            Rego,Make,BodyType,Seats, Colour,Cost
            returns with format:
            Rego     Model    Body    Seats    Colour     Price Per Day      Location     Returned (y/n)
        """
        print("Search By: ")
        print("1. Rego")
        print("2. Make")
        print("3. Body type")
        print("4. Seats")
        print("5. Colour")
        print("6. Cost Per Day")
        print("7. Back")
        #various search types from atrributes
        attribute = None
        running = True
        while(running):
            try:
                choice = int(input("> "))
            except ValueError:
                print("Please enter number within menu options")
            else:
                if choice > 6 or choice <= 0:
                    print("Please enter number within menu options")
                else:
                    if choice == 1:
                        attribute = "Rego"
                        running = False
                    elif choice == 2:
                        attribute = "Make"
                        running = False
                    elif choice == 3:
                        attribute = "Body"
                        running = False
                    elif choice == 4:
                        attribute = "Seats"
                        running = False
                    elif choice == 5:
                        attribute = "Colour"
                        running = False
                    elif choice == 6:
                        attribute =  "CostPerDay"
                        running = False
                    elif choice == 7:
                        running = False
                        #get car attribute
        if attribute is not None:
            term = input("\nEnter " + attribute + ": ")
            with DatabaseUtils() as db:
                self.searchCars = db.searchCars(attribute,term)

            data = ["Rego","Make","Body","Seats","Colour","Cost Per Day($)","Location","Returned"]        
            row_format ="{:<17}"*(len(data))
            print(row_format.format(*data))
            for car in self.searchCars: #return formatted string as car table
                print(row_format.format(car[0],car[1],car[2],str(car[3]),car[4],str(car[5]),str(car[6]),str(car[7])))
        else:
            print("No record of car")

        self.printMenu()
        
    
    def bookCar(self):
        """
            allows logged in user to book car given rego number, prompts for dates and creates calendar event
        """
        
        rego = input("Enter Rego: ")
        regex = re.compile("([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$")

        validDate = False
        while validDate == False:
            startDate = input("Input Booking Start Date (YYYY-MM-DD): ")
            endDate = input("Input Booking End Date (YYYY-MM-DD): ")
            if (regex.match(startDate) and regex.match(endDate)): #check input is in date format
                startYear, startMonth, startDay = startDate.split('-')
                startDate = datetime.date(int(startYear), int(startMonth), int(startDay))
                #get user date data to create booking
                endYear, endMonth, endDay = endDate.split('-')
                endDate = datetime.date(int(endYear), int(endMonth), int(endDay))
                if (endDate < startDate):
                    print("\nError: End Booking Date is Before Start Start\n")
                else:
                    validDate = True
            else:   #date validation check
                print("\nInvalid Dates, Please Try Again\n")
        

        with DatabaseUtils() as db:
                self.userEmail = db.getUserEmail(self.user)
                eventID = rego
                #confirmed booking can be created and calendar event is also created
                eventID = CalendarUtils().createEvent(self.user, self.userEmail, rego, startDate, endDate)
                if(db.bookCar(self.user, rego.upper(), startDate, endDate, eventID)):
                    print("Your Booking ID is: " + eventID)
                else:   
                    print("Sorry, Booking already exists for booking date")
        self.printMenu()

    def cancelBooking(self):
        """
            allows user to cancel booking given their booken id when prompted
        """
        eventID = input("Enter Booking ID. : ")
        try:   #delete booking given ID from both calendar and DB
            CalendarUtils().deleteEvent(eventID)
            with DatabaseUtils() as db:
                db.deleteBooking(eventID)
        except:
            print("\nError: Booking Doesnt Exist")
        self.printMenu()
        

class AdminMenu(CustomerMenu):
    
    def start(self,user):
        """
            alternate start menu for admin account
        """
         #cleans terminal for new menu
        print(chr(27) + "[2J")
        running = True
        print("\nWelcome "+user+"\n")
        self.printMenu()
        self.user = user
        #start menu display and assure database is up to date
        with DatabaseUtils() as db:
            self.cars = db.getAllCars()
            self.userList = db.getUsers()
            if not self.cars:
                db.populateDatabase()
                self.cars = db.getAllCars()

        while(running):
            try:
                choice = int(input("> "))
            except ValueError:
                print("Please enter number within menu options")
            else:
                if choice > 7 or choice <= 0:
                    print("Please enter number within menu options")
                else:   #get user input
                    if choice == 1:
                        self.rentalHistory()
                    elif choice == 2:
                        self.search()
                    elif choice == 3:
                        self.updateCar()
                    elif choice == 4:
                        self.updateUsers()
                    elif choice == 5:
                        self.reportFault()
                    elif choice == 6:
                        self.showCarLocations()
                    elif choice == 7:
                        running = False
                        print("Thank you")
    
    def rentalHistory(self):
        """
            view rental history of a vehicle
        """
        print("Rental History:")
        rego = input("Enter Rego: ")
        
        with DatabaseUtils() as db:
            self.bookings = db.admin_getBookingHistory(rego)
        if self.bookings:
            data = ["Rego", "Booking ID", "UserID", "Start Date", "Finish Date"]
            row_format ="{:<17}"*(len(data))
            print(row_format.format(*data))
            for bookings in self.bookings:
                print(row_format.format(str(bookings[0]),bookings[1],str(bookings[2]),str(bookings[3]),str(bookings[4])))
        else:
            print("No bookings found \n")
        self.printMenu()


    def search(self):
        print("search:")
        print("1. Cars")
        print("2. Users")
        print("3. return")
        searching = True
        while(searching):
            try:
                choice = int (input("> "))
            except ValueError:
                print("Please enter number within menu options")
            else:
                if choice > 3 or choice <= 0:
                    print("Please enter number within menu options")
                else:
                    if choice == 1:
                        print("\n")
                        self.searchCars()
                        searching = False
                    elif choice == 2:
                        self.searchUser()
                        searching = False
                    elif choice == 3:
                        searching = False
                        self.printMenu()

        

    def searchUser(self):
        """
            admin ability to search user
        """
        print("Search by: ")
        print("1. User ID")
        print("2. Email Address")
        print("3. Name")
        print("4. User type")

        attribute = None
        running = True

        while(running):
            try:
                choice = int(input("> "))
            except ValueError:
                print("Please enter number within menu options")
            else:
                if choice > 4 or choice <= 0:
                    print("Please enter number within menu options")
                else:
                    if choice == 1:
                        attribute = "UserID"
                        running = False
                    elif choice == 2:
                        attribute = "Email"
                        running = False
                    elif choice == 3:
                        attribute = "Name"
                        running = False
                    elif choice == 4:
                        attribute = "UserType"
                        running = False

        if attribute is not None:

            if attribute == "UserType":
                print("1. customer\n2. admin\n3. manager\n4. engineer\n")
                choosing = True
                while(choosing):
                    try:
                        choice = int(input("> "))
                    except ValueError:
                        print("Please enter number within user options")
                    else:
                        if choice > 3 or choice <= 0:
                            print("Please enter number within user options")
                        else:
                            if choice == 1:
                                term = "CUSTOMER"
                                break
                            elif choice == 2:
                                term = "ADMIN"
                                break
                            elif choice == 3:
                                term = "MANAGER"
                                break
                            elif choice == 4:
                                term = "ENGINEER"
                                break
            else:
                term = input("\nEnter " + attribute + ": ")

            with DatabaseUtils() as db:
                self.searchUsers = db.searchUsers(attribute,term)

            data = ["UserID","Name","Email","User Type"]        
            row_format ="{:<17}"*(len(data))
            print(row_format.format(*data))
            for user in self.searchUsers:
                print(row_format.format(str(user[0]),str(user[1]),str(user[2]),str(user[4])))
        else:
            print("No record of user")

        self.printMenu()



    def updateCar(self):
        """
            update or delete any part of the car database
        """
        rego = input("Enter rego: ")
        with DatabaseUtils() as db:
            car = db.searchCars("rego", rego)
            if car:
                print("1. Edit %s?" % rego)
                print("2. Delete %s?" % rego)
                choosing = True
                while(choosing):
                    try:
                        choice = int(input("> "))
                    except ValueError:
                        print("incorrect value")
                    else:
                        if choice == 1:
                            print("Edit: \n1. Make\n2. Body\n3. Seats\n4. Colour\n5. Cost per day")
                            running = True
                            while(running):
                                try:
                                    choice = int(input("> "))
                                except ValueError:
                                    print("Please enter number within menu options")
                                else:
                                    if choice > 5 or choice <= 0:
                                        print("Please enter number within menu options")
                                    else:
                                        if choice == 1:
                                            attribute = "Make"
                                            running = False
                                        elif choice == 2:
                                            attribute = "Body"
                                            running = False
                                        elif choice == 3:
                                            attribute = "Seats"
                                            running = False
                                        elif choice == 4:
                                            attribute = "Colour"
                                            running = False
                                        elif choice == 5:
                                            attribute =  "CostPerDay"
                                            running = False
                                            #get car attribute
                                if attribute is not None:
                                    print("Enter new %s data: " % attribute)
                                    editing = True
                                    valid = False
                                    while(editing):
                                        newData = input()
                                        if(attribute == "Seats"):
                                            try:
                                                newData = int(newData)
                                            except ValueError:
                                                print("incorrect value type")
                                            else:
                                                valid = True
                                                break
                                        if(attribute == "CostPerDay"):
                                            try:
                                                newData = newData
                                            except ValueError:
                                                print("incorrect value type")
                                            else:
                                                valid = True
                                                break
                                        else:
                                            valid = True
                                            break
                                    if valid:
                                        with DatabaseUtils() as db:
                                            if db.updateCar(rego,attribute,newData):
                                                print("%s updated.\n" % rego)
                                            else:
                                                print("Error with update data, please try again.")
                                            choosing = False
                                    break

                             
                        elif choice == 2:
                            print("Are you sure you wish to delete car %s?" % rego)
                            print("enter y/n")
                            while True:
                                choice = input("> ")
                                if choice == "y":
                                    with DatabaseUtils() as db:
                                        db.deleteCar(rego)
                                    print("%s deleted\n" % rego)
                                    choosing = False
                                    break
                                elif choice == "n":
                                    choosing = False
                                    break

                            else:
                                print("incorrect value")

            else:
                print("car does not exist, create new? y/n")
                while True:
                    choice = input("> ")
                    if(choice == 'y'):
                        print("create car for rego %s:" % rego)
                        manufacturer = input("Manufacturer: ")
                        body = input("body: ")
                        seats = int(input("seats: "))
                        colour = input("colour: ")
                        cost = input("cost per day ($): ")
                        with DatabaseUtils() as db:
                            if db.addCar(rego,manufacturer,body,seats,colour,cost):
                                print("Car added")
                            else:
                                print("error with car data")
                        break
                    elif(choice == 'n'):
                        break


        self.printMenu()

    def updateUsers(self):
        """
            update or delete part of the user accounts
        """
        print("Users:")
        username = input("Enter username: ")
        with DatabaseUtils() as db:
            user = db.searchUsers("Name", username)
            if user:
                print("1. Edit %s?" % username)
                print("2. Delete %s?" % username)
                choosing = True
                while(choosing):
                    try:
                        choice = int(input("> "))
                    except ValueError:
                        print("incorrect value")
                    else:
                        if choice == 1:
                            print("Edit: \n1. Name\n2. Email\n3. Password\n4. User Type\n")
                            running = True
                            while(running):
                                try:
                                    choice = int(input("> "))
                                    if choice > 4 or choice <= 0:
                                        print("Please enter number within menu options")
                                    else:
                                        if choice == 1:
                                            attribute = "Name"
                                            running = False
                                        elif choice == 2:
                                            attribute = "Email"
                                            running = False
                                        elif choice == 3:
                                            attribute = "Password"
                                            running = False
                                        elif choice == 4:
                                            attribute = "UserType"
                                            running = False
                                except ValueError:
                                        print("Please enter number within menu options")

                                            #get car attribute
                                if attribute is not None:
                                    print("Enter new %s data: " % attribute)
                                    editing = True
                                    valid = False
                                    while(editing):
                                        if(attribute == "UserType"):
                                            print("Change to:\n1. Engineer\n2. Admin\n3. Manager\n4. Customer")
                                            userType = int(input("> "))
                                            if(userType == 1):
                                                newData = "ENGINEER"
                                                valid = True
                                                break
                                            elif(userType == 2):
                                                newData = "ADMIN"
                                                valid = True
                                                break
                                            elif(userType == 3):
                                                newData = "MANAGER"
                                                valid = True
                                                break
                                            elif(userType == 4):
                                                newData = "CUSTOMER"
                                                valid = True
                                                break
                                        elif(attribute == "Password"):
                                            newData = input("New Password: ")
                                            newData = sha256_crypt.hash(newData)
                                            valid = True
                                            break
                                        else:
                                            newData = input("> ")
                                            valid = True
                                            break
                                    if valid:
                                        with DatabaseUtils() as db:
                                            if db.updateUser(username,attribute,newData):
                                                print("%s updated.\n" % username)
                                            else:
                                                print("Error with update data, please try again.")
                                            choosing = False
                                    break

                             
                        elif choice == 2:
                            print("Are you sure you wish to delete User %s?" % username)
                            print("enter y/n")
                            while True:
                                choice = input("> ")
                                if choice == "y":
                                    with DatabaseUtils() as db:
                                        db.deleteUser(username)
                                    print("%s deleted\n" % username)
                                    choosing = False
                                    break
                                elif choice == "n":
                                    choosing = False
                                    break

                            else:
                                print("incorrect value")

            else:
                print("User does not exist, create new? y/n")
                while True:
                    choice = input("> ")
                    if(choice == 'y'):
                        print("create user with name %s:" % username)
                        email = input("email: ")
                        password = input("password: ")
                        while True:
                            print("Create as:\n1. Engineer\n2. Admin\n3. Manager\n4. Customer")
                            userType = int(input("> "))
                            if(userType == 1):
                                userType = "ENGINEER"
                                valid = True
                                break
                            elif(userType == 2):
                                userType = "ADMIN"
                                valid = True
                                break
                            elif(userType == 3):
                                userType = "MANAGER"
                                valid = True
                                break
                            elif(userType == 4):
                                userType = "CUSTOMER"
                                valid = True
                                break
                        
                        with DatabaseUtils() as db:
                            if db.insertUser(username,email,password,userType):
                                print("User added")
                            else:
                                print("error with user data")
                        break
                    elif(choice == 'n'):
                        break
        self.printMenu()

    def reportFault(self):
        """
            report fault with given rego.
            optionally sends fault to engineer via pushbullet
        """
        print("Report Fault:")
        with DatabaseUtils() as db:
            rego = input("Enter rego of faulty vehicle: ")

            cars = db.searchCars("Rego",rego)
            if cars:
                fault = input("Please provide description of fault for %s: " % rego)
                if db.reportFault(rego,fault):
                    locations = db.getCarLocations()
                    for location in locations:
                        if location[0] == rego:
                            fault = fault + "\nVehicle located at {}".format(location[1])
                        
                    print("Fault reported on and location recorded for %s, assign engineer? y/n" % rego)
                    while True:
                        send = input("> ")
                        if send == "y":
                            pushbullet = PushbulletAccess() #send via pushbullet to account
                            if pushbullet.send_notification(rego,fault):
                                print("Notification sent")
                                break
                            else:
                                print("Fault reported\nhowever error in notifying engineer.")
                                break
                        elif send == "n":
                            print("Fault reported. No notifcation sent.")
                            break
                        else:
                            print("please enter y/n")
                        
                else:
                    print("Error in reporting fault.")
            else:
                print("No such rego exists")

        self.printMenu()
        

    def showCarLocations(self):

        with DatabaseUtils() as db:
            self.carLocations = db.getCarLocations()
        
        url = "http://maps.google.com/maps/api/staticmap?size=1280x1280&scale=2&markers=size:small|color:blue|"
        
        for car in self.carLocations:
            url = url + car[1] + "|"
        
        url = url + "&key=KEY"

        print("\nCar Locations: " + url)

        img = requests.get(url).content
        currDate = str(date.today())
        try:
            filename = "maps/" + currDate + ".png"
            with open(filename, 'wb') as handler:
                handler.write(img)
        except:
            filename = "MasterPi/maps/" + currDate + ".png"
            with open(filename, 'wb') as handler:
                handler.write(img)


        print("\nNew Map Picture Added to MasterPi/maps directory")

        self.printMenu()

        
    def printMenu(self):
        """
            generic print statement for menu.
            function reused throughout class
        """
        print("\nMenu:\n")
        print("1. View car rental history")
        print("2. Search")
        print("3. Add/Remove/Update Car")
        print("4. Add/Remove/Update User")
        print("5. Report Car Faults")
        print("6. Create Car Map")
        print("7. Logout\n")