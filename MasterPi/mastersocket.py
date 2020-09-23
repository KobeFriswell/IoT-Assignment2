import socket
import sys
from passlib.hash import sha256_crypt
from databaseaccess import DatabaseUtils

#master pi socket acting as receiver
class MasterSocket:
    """
        Socket class to create new listener socket to receive
        data from agent Pi's. Ran on seperate thread in background to UI.
        Socket listens on repeat. Initialised at start of program.
        
        If receiving RETURN, database is updated that the agent pi has been locked and returned.
        if receiving unlock request, database is checked off against received credentials and a
        T or F (True or False) is sent dependent on whether credential check was successful
    """
    
    def start(self):
        #initalise socket
        master = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_address= ('localhost',10000)
        print('starting up on {} port {}'.format(*server_address))
        master.bind(server_address)
        
        while True:
            #listen for incoming data from agent pi's
            master.listen(1)
            data = None
            while True:
                connection,client_address = master.accept()
                try:
                    while True:
                        data = connection.recv(100)
                        if data:
                            string = data.decode('utf-8')

                            if string[0:6] == 'RETURN': #first return type: returning car
                                rego = string[7:13] #update db that car is unavailable 
                                print('(Car returned: {}) Returning to UI..\n> '.format(rego),end="")
                                connection.sendall('T'.encode('utf-8'))
                                with DatabaseUtils() as db:
                                    db.returnCar(str(rego))
                            elif string[0:4] == 'REGO':
                                rego = string[5:11]
                                with DatabaseUtils() as db:
                                    cars = db.searchCars("rego",rego)
                                    if cars:
                                        connection.sendall('T'.encode('utf-8'))
                                    else:
                                        connection.sendall('F'.encode('utf-8'))
                            elif string[0:8] == 'LOCATION':
                                splitString = string.split("_")
                                carRego = splitString[1]
                                latitude = splitString[2]
                                longitude = splitString[3]

                                #Create string with both long and lat for db
                                location = latitude + "," + longitude

                                with DatabaseUtils() as db:
                                    if (db.addCarLocation(carRego, location)): #Return a 'T' if the db is updated succesfully
                                        print("\n(car {} location has been updated) Returning to UI.. \n> ".format(carRego),end="")
                                        connection.sendall('T'.encode('utf-8'))
                                        found = True
                                    else: #If it cannot update the db successfully
                                        connection.sendall('F'.encode('utf-8'))
                                        print('\n(car {} has had attempted to update location) Returning to UI..\n> '.format(carRego),end="")
                            else:
                                rego=string[0:6] #second return type, taking car
                                username = string[string.find('_user:')+6:string.find('_pass:')-1]
                                password = string[string.find('_pass:')+6:string.find('_date:')-1]
                                date = string[string.find('_date:')+6:len(string)]
                                found = False   #check database that user login details are correct
                                with DatabaseUtils() as db:
                                    if(db.checkoutBooking(username,password,rego,date)):
                                        print('\n(car {} has been unlocked) Returning to UI..\n> '.format(rego),end="")
                                        connection.sendall('T'.encode('utf-8'))
                                        found = True
                                    else:   #in event details are incorrect, update admin that car has had attempted access
                                        connection.sendall('F'.encode('utf-8'))
                                        print('\n(car {} has had attempted access) Returning to UI..\n> '.format(rego),end="")
                        else:
                            break
                finally:
                    connection.close()
