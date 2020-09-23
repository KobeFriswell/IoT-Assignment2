import MySQLdb
from passlib.hash import sha256_crypt
from datetime import datetime

class DatabaseUtils:
    """
        General class holding functions to allow access to google cloud database.
    """

    

    #appropriate connection details for Google Cloud database
    HOST = "HOST"
    USER = "USERNAME"
    PASSWORD = "PASSWORD"
    DATABASE = "DB-NAME"

    def __init__(self, connection = None):

        if(connection == None):
            connection = MySQLdb.connect(DatabaseUtils.HOST, DatabaseUtils.USER,
                DatabaseUtils.PASSWORD, DatabaseUtils.DATABASE)
        self.connection = connection
        #connect to database when initialised
    def close(self):
        self.connection.close()
        #close connection upon request
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def createDatabase(self):
        """
            function to create database in the event that it doed not exist
        """
        with self.connection.cursor() as cursor:
            #initialise user table
            
            #uncomment for manual reset
            #cursor.execute("""drop table Users;""")
            #cursor.execute("""drop table Engineers;"""),

            #self.connection.commit()

            cursor.execute("""
                create table if not exists Users (
                    UserID int not null auto_increment,
                    Name text not null,
                    Email text not null,
                    Password text not null,
                    UserType text not null,
                    constraint PK_Users primary key (UserID)
                    );
                    
                      """)
            self.connection.commit()

            #seperate database for engineer and their mac address
            cursor.execute("""
                create table if not exists Engineers (
                    EngineerID int not null auto_increment,
                    EngineerMAC text not null,
                    UserID int not null,
                    constraint PK_Engineers primary key (EngineerID)
                );
                """)
            self.connection.commit()

            #initialise car table

            #uncomment for manual reset
            #cursor.execute("""drop table Cars;""")
            #self.connection.commit()
            
            cursor.execute("""
                create table if not exists Cars (
                    Rego text not null,
                    Make text not null,
                    Body text not null,
                    Seats int not null,
                    Colour text not null,
                    CostPerDay Double(5,2) not null, /*Values between $000.01 and $999.99*/
                    Location varchar(255) Default '-37.8081201,144.9622256', /*RMIT university as default*/
                    Returned text not null,
                    Fault varchar(255) Default 'NONE',
                    constraint PK_Cars primary key (Rego(6))
                    );
                
                  """)
            self.connection.commit()
            #initialise Bookings table
            cursor.execute("""
                create table if not exists Bookings (
                    BookingID int not null auto_increment,
                    UserID int not null,
                    Rego text not null,
                    StartDate DATE not null,
                    EndDate DATE not null,
                    EventID text not null,
                    constraint PK_Bookings primary key (BookingID)
                    );
                 
                 """)
            self.connection.commit()
                 
    def populateDatabase(self):
        """
            populates Car table with company cars
        """
        #preset company cars added to car database in event of data loss
        with self.connection.cursor() as cursor:
            cursor.execute("""
            insert into Cars (Rego,Make,Body,Seats,Colour,CostPerDay,Returned)
                 values
                     ('GUX414','Volkswagen','sedan',5,'red',90.50,'True'),
                     ('JQC232','BMW','sedan',5,'white',110.25,'True'),
                     ('APO810','Mazda','SUV',5,'black',102.50,'True'),
                     ('FHO156','Jeep','SUV',6,'silver',105.00,'True'),
                     ('JRY328','Holden','hatch',5,'white',80.50,'True'),
                     ('AIE357','Mazda','convertible',3,'red',120.00,'True'),
                     ('EFG432','Volkswagen','hatch',5,'white',100.00,'True'),
                     ('AAE122','Mercedes','luxury',4,'back',130.50,'True'),
                     ('RET332','Holden','SUV',6,'black',110.75,'True'),
                     ('AWE032','Porsche','luxury',4,'silver',140,'True'),
                     ('RET331','Ford','classic',3,'blue',160,'True'),
                     ('GRT044','Ford','sedan',5,'blue',110,'True');       
                     """)
            self.connection.commit()
                    
    def getAllCars(self):
        """
            return all cars
        """
        with self.connection.cursor() as cursor:
            cursor.execute("select Rego,Make,Body,Seats,Colour,CostPerDay,Location from Cars")
            return cursor.fetchall() #return all car data

    def insertUser(self, name,email,password,userType):
        """
            insert new user into User table given name, email and password
        """
        with self.connection.cursor() as cursor:
            cursor.execute("insert into Users (Name,Email,Password,UserType) values (%s,%s,%s,%s)", (name,email,password,userType,))
        self.connection.commit()

        return cursor.rowcount == 1

    def getUsers(self):
        """
            return all users
        """
        with self.connection.cursor() as cursor:
            cursor.execute("select Name,Password,UserType from Users")
            return cursor.fetchall() #return all users and encrypted passwords

    def checkoutBooking(self, username, password, carRego, date):
        """
            allows user to unlock and take car given username, password and car rego are correct
            and todays date is within their booking time frame
        """
        with self.connection.cursor() as cursor:
            try:
                cursor.execute("""select UserID,Name,Password
                                from Users
                                where Name=%s""",[username])
                userdata = cursor.fetchall()   #first check user details and password are verified
                if(username == userdata[0][1] and sha256_crypt.verify(password,userdata[0][2])):
                    today = datetime.today().strftime('%Y-%m-%d') #second check that today is between start and end date of booking
                    cursor.execute("""select Rego,StartDate,EndDate
                                    from Bookings
                                where userID = %s AND %s between StartDate and EndDate""",([userdata[0][0]],[today],))
                    bookingData = cursor.fetchall()
                    
                    if(bookingData[0][0] == carRego): #update database that car has been taken
                        cursor.execute("""update Cars
                                                set Returned = 'False'
                                                where Rego like %s""",[carRego])
                        self.connection.commit()
                        return True #allow acccess
            except:
                return False
            
        return False #refuse access
    
    def returnCar(self,carRego):
        """
            given a car registration, it updates the Car table whether a car has been returned
        """
        with self.connection.cursor() as cursor:
            cursor.execute("""update Cars
                            set Returned = 'True'
                            where Rego like %s""",[carRego])
            self.connection.commit()    #update database that car has been returned
                                                
    
    def createBooking(self,user,rego,startDate,EndDate):
        """
                create new booking for a user within the Booking table given
                user, rego, start date and end date of booking.
        """
        with self.connection.cursor() as cursor:
            cursor.execute("""insert into Bookings (UserID,Rego,StartDate,EndDate) values (%s,%s,%s,%s)""", (user,rego,startDate,EndDate,))
            cursor.execute("""select BookingID from Bookings where UserID = %s and Rego = %s and StartDate = %s""",(user,rego,startDate,))
            print("Booking {} created".format(cursor.fetchall[0][0]))   #insert all data for booking into database
            self.connection.commit()
            
            
    def removeBooking(self,bookingID):
        """
            Removes booking given a bookingID
        """
        with self.connection.cursor() as cursor:
            cursor.execute("""select BookingID from Bookings where BookingID = %s""",[bookingID])
            if(cursor.fetchall()[0][0] == bookingID):
                cursor.execute("""delete from Bookings where BookingID = %s""",[bookingID])
                self.connection.commit()
                print("Booking %s deleted",[bookingID]) #remove all data from database for parsed booking
            else:
                print("booking not found")
            

    def getBookingHistory(self, user):
        """
            returns all bookings for a given user
        """
        with self.connection.cursor() as cursor:
            cursor.execute("""select BookingID, Rego, StartDate, EndDate 
                            from Bookings inner 
                            join Users ON Users.UserID=Bookings.UserID where Users.Name=%s""", [user])
            return cursor.fetchall()    #get all bookings history based on userID
    
    def admin_getBookingHistory(self, rego):
        """
            returns all bookings for a given car
        """
        with self.connection.cursor() as cursor:
            cursor.execute("""select Rego, BookingID, UserID, StartDate, EndDate 
                            from Bookings where rego like %s""", [rego])
            return cursor.fetchall()    #get all bookings history based on userID


    def searchCars(self, attribute, term):
        """
            returns all cars given string attribute (fixed from call) and term
        """
        with self.connection.cursor() as cursor: 
            query = "select * from Cars where {} like '{}'".format(attribute,term)
            cursor.execute(query)
            return cursor.fetchall() #return car based on attribute check

    def searchUsers(self, attribute, term):
        """
            returns all cars given string attribute (fixed from call) and term
        """
        with self.connection.cursor() as cursor: 
            query = "select * from Users where {} = '{}'".format(attribute,term)
            cursor.execute(query)
            return cursor.fetchall() #return car based on attribute check


    def getAvailableCars(self, date):
        """
            retursn all available cars given date
        """
        with self.connection.cursor() as cursor:
            cursor.execute("""select *
                            from Cars
                            where rego not in(select rego from Bookings 
                                            where %s between StartDate and EndDate) and Fault like 'NONE'""", [date])
            return cursor.fetchall() #return all cars where car hasnt been booked on todays date
    
    def getUserID(self, user):
        """
            returns userID given username
        """
        with self.connection.cursor() as cursor:
            cursor.execute("select UserID from Users where Name=%s", [user])
            return cursor.fetchall() #return specific user ID based on username

    def getUserEmail(self, user):
        """
            returns userEmail given username
        """
        with self.connection.cursor() as cursor:
            cursor.execute("select Email from Users where Name=%s", [user])
            return cursor.fetchall() #get users email

    def bookCar(self, user, rego, startDate, endDate, eventID):
        """
            allows car to be booked and updates booking database given username, rego, start and enddates. also takes eventID to update calendar
        """
        with self.connection.cursor() as cursor:
            cursor.execute("select * from Bookings where Rego=%s and ((%s between StartDate and EndDate) or (%s between StartDate and EndDate))", (rego,startDate,endDate))
            bookings = cursor.fetchall() 

        #If no bookings for rego and specific date, add booking
        if not bookings:
            userID = self.getUserID(user)
            with self.connection.cursor() as cursor:
                cursor.execute("insert into Bookings (UserID,Rego,StartDate,EndDate,EventID) values (%s,%s,%s,%s,%s)", (userID,rego,startDate,endDate,eventID))
                self.connection.commit()
            return True
        
        #Else return false for bookings
        else:
            return False

    def deleteBooking(self, eventID):
        """
            removes booking from database given ID
        """
        with self.connection.cursor() as cursor:
            cursor.execute("delete from Bookings where EventID = %s", [eventID])
            self.connection.commit()

    def deleteCar(self, rego):
        """
            admin request to delete car
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("delete from Cars where Rego like %s", [rego])
                self.connection.commit()
                return True
        except:
            return False
        return False

    def addCar(self, rego, make, body, seats, colour, costPerDay):
        with self.connection.cursor() as cursor:
            try:
                
                executable = """
                insert into Cars (Rego,Make,Body,Seats,Colour,CostPerDay,Returned)
                values ('{}','{}','{}',{},'{}',{},'True');""".format(rego,make,body,seats,colour,costPerDay)
                cursor.execute(executable)
                self.connection.commit()
                return True
            except:
                return False
        return False

    def updateCar(self,rego,attribute,newData):
        """
            admin request to update data
        """
        with self.connection.cursor() as cursor:
            try:
                if(attribute == "CostPerDay" or attribute == "Seats"):
                    execution = """
                                    update Cars
                                    set {} = {}
                                    where Rego like '{}';
                                """.format(attribute,newData,rego)
                else:
                    execution = """update Cars set {} = '{}' where Rego like '{}';""".format(attribute,newData,rego)
                cursor.execute(execution)
                self.connection.commit()
                return True
            except:
                return False
        return False

    def updateUser(self,name,attribute,newData):
        """
            admin request to update data
        """
        with self.connection.cursor() as cursor:
            try:
                execution = """update Users set {} = '{}' where Name like '{}';""".format(attribute,newData,name)
                cursor.execute(execution)
                self.connection.commit()
                return True
            except:
                return False
        return False

    def deleteUser(self, name):
        """
            admin request to delete user
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("delete from Users where Name like %s", [name])
                self.connection.commit()
                return True
        except:
            return False
        return False

    def fixFault(self,rego):
        """
            reset fault of car when repaired
        """
        with self.connection.cursor() as cursor:
            try:
                cursor.execute("update Cars set Fault = 'NONE' where Rego like '{}'",[rego])
                self.connection.commit()
                return True
            except:
                return False
        return False



    def reportFault(self,rego,fault):
        """
            report fault of given car rego
        """
        with self.connection.cursor() as cursor:
            try:
                execution = """update Cars set Fault = '{}' where Rego like '{}';""".format(fault,rego)
                cursor.execute(execution)
                self.connection.commit()
                return True
            except:
                return False
        return False
    
    def addCarLocation(self, rego, location):
        """
            Adds location for car in car table
        """
        with self.connection.cursor() as cursor:
            try:
                execution = """update Cars set Location = '{}' where Rego like '{}';""".format(location,rego)
                cursor.execute(execution)
                self.connection.commit()
                return True
            except:
                return False
        return False

    def getCarLocations(self):
        """
            Returns the locations of all the cars
        """
        with self.connection.cursor() as cursor:
            cursor.execute("select Rego, Location from Cars where Location is not null")
            return cursor.fetchall()
