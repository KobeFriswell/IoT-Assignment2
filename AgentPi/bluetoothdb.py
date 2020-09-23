import MySQLdb
from passlib.hash import sha256_crypt
from datetime import datetime

class DatabaseUtils:
#    """
#       General class holding functions to allow access to google cloud database.
#    """
#	appropriate connection details for Google Cloud database
    	HOST = "35.197.176.186"
    	USER = "root"
    	PASSWORD = "IHkoFeHgmh085ly9"
    	DATABASE = "Assignment2"

        def __init__(self, connection = None):
                if(connection == None):
                        connection = MySQLdb.connect(DatabaseUtils.HOST, DatabaseUtils.USER, DatabaseUtils.PASSWORD, DatabaseUtils.DATABASE)
                self.connection = connection
                #connect to database when initialised
        def close(self):
                self.connection.close()
                #close connection upon request
        def __enter__(self):
                return self

        def __exit__(self, type, value, traceback):
                self.close()

        def getMacAddress(self, ListMacAddress):
                with self.connection.cursor() as cursor:
                    Query='select * from Engineers where EngineerMAC in (\'%s\')' % ListMacAddress
#                    print(Query)
                    cursor.execute(Query)
                    return cursor.fetchall()
