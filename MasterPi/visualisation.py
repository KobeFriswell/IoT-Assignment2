
import matplotlib.pyplot as plt
import MySQLdb
import pandas as pd

class visualisation:
    
    def __init__ (self):
        #mySQLDB connection string
        self.conn = MySQLdb.connect(host="HOST", user="USERNAME", password="PASSWORD",database="DB-NAME")
        self.cursor = self.conn.cursor()
        
    def carFault(self):
        #displays a bar graph showing the make of the cars and the number of faults it has
        df = pd.read_sql('SELECT * FROM Cars', self.conn)
        group_by_make = df.groupby(by=['Make'])
        car_data_count = group_by_make.count()
        plot_carFault = car_data_count.plot(kind='bar', y='Fault')
        plt.show()         
    
    def carPrice(self):
        # display the costPerDay of the make with a scatter plot
        df = pd.read_sql('SELECT * FROM Cars', self.conn)
        plot_price = df.plot(kind ='scatter', y ='CostPerDay', x='Make')
        plt.show()
        
    def avgCost(self):
        # displays the average cost per day of the make with a line graph
        df = pd.read_sql('SELECT * FROM Cars', self.conn)
        group_by_make = df.groupby(by=['Make'])
        car_data_mean = group_by_make.mean()
        carPrice = car_data_mean['CostPerDay']
        plt.plot(carPrice)
        plt.xlabel('Car Make')
        plt.ylabel('Cost Per Day')
        plt.title('Average Cost per day')
        plt.show()
        
            
    
    
