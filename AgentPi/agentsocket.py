import socket
import sys
from datetime import date
class SocketAccess():
    """
        SocketAccess allows the Agent Pi to send data to the master for unlock and return data.
        new sockets created on running of SocketAccess functions.
    """
    # Agent socket acting as Sender
    def returnCar(self,carRego):
        """
            return socket, allowing basic data to be sent to the Master Pi (sends registration taken as passed value carRego)
            returns True if received correctly by master pi and false if not.
        """
        result = False
        try:
            #Create TCP/IP
            agent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect the socket to the port
            server_address = ('localhost',10000)
            print('connecting to {} port {}'.format(*server_address))
            agent.connect(server_address)
            # Send data
            today = date.today()
            message = 'RETURN_{}'.format(carRego)
            agent.sendall(message.encode('utf-8'))
            print('updating MasterPi..')
            amount_received = 0
            amount_expected = 1
            while amount_received < amount_expected:
                data = agent.recv(50)
                amount_received += len(data)

                if data == b'T': #returned true
                    result = True
                elif data == b'F':
                    result = False
        except:
            print("connection could not be made")
        finally:
            agent.close()
        
        return result
        

    def loginCheck(self,username,password,carRego):
        """
            sends credentials to master pi by creating new socket and sending passed values (username, password, carRego)
            returns true if credentials check off correctly within masterPi's databaseAccess.
            Else returns false.
        """
        result = False
        try:
            #Create TCP/IP
            agent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect the socket to the port
            server_address = ('localhost',10000)
            print('connecting to {} port {}'.format(*server_address))
            agent.connect(server_address)

            # Send data
            today = date.today()
            message = '{} _user:{} _pass:{} _date:{}'.format(carRego,username,password,today)
            agent.sendall(message.encode('utf-8'))
            print('sending credentials..')
            amount_received = 0
            amount_expected = 1

            while amount_received < amount_expected:
                data = agent.recv(50)
                amount_received += len(data)

                if data == b'T': #returned true
                    result = True
                elif data == b'F':
                    result = False
        except:
            print("connection could not be made")   
        finally:
            agent.close()
            
        return result
    
    def sendLocation(self, rego, location):

        """
            sends  car location to master pi by creating new socket and sending passed long and lat
            returns true if location is successfully added to the database.
            Else returns false.
        """
        result = False
        try:
            #Create TCP/IP
            agent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect the socket to the port
            server_address = ('localhost',10000)
            print('connecting to {} port {}'.format(*server_address))
            agent.connect(server_address)

            # Send data
            message = 'LOCATION_{}_{}_{}'.format(rego, location[0], location[1])
            agent.sendall(message.encode('utf-8'))
            print('Updating MasterPi Car Location..')
            amount_received = 0
            amount_expected = 1
            while amount_received < amount_expected:
                data = agent.recv(50)
                amount_received += len(data)

                if data == b'T': #returned true
                    result = True
                elif data == b'F':
                    result = False
        except:
            print("connection could not be made")
        finally:
            agent.close()
        
        return result

    def checkCar(self,carRego):
        """
            sends credentials to master pi by creating new socket and sending passed value carRego
            returns true if credentials check off correctly within masterPi's databaseAccess.
            Else returns false.
        """
        result = False
        try:
            #Create TCP/IP
            agent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect the socket to the port
            server_address = ('localhost',10000)
            print('connecting to {} port {}'.format(*server_address))
            agent.connect(server_address)

            # Send data
            today = date.today()
            message = 'REGO_{}'.format(carRego)
            agent.sendall(message.encode('utf-8'))
            print('sending credentials..')
            amount_received = 0
            amount_expected = 1

            while amount_received < amount_expected:
                data = agent.recv(50)
                amount_received += len(data)

                if data == b'T': #returned true
                    result = True
                elif data == b'F':
                    result = False
        except:
            print("connection to master could not be made, rego not verified")   
        finally:
            agent.close()
            
        return result