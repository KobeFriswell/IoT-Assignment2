import agentmenu
from agentsocket import SocketAccess
#main file. only file to be directly ran by terminal
def main():
    """
        Runs AgentPi by calling on menu with unique carRegistration. Checked off on local list.
    """
    carRego = input("enter car's registration number: ")
    #locally stores rego's to check that choosen car is registered in google db
    #if car is part of db, start menu for user

    sc = SocketAccess()
    if sc.checkCar(carRego):
        print("Car in database. Continue..")
        menu = agentmenu.Menu(carRego)
        menu.start()
    else:
        print("Rego does not exist in master pi database or master pi is not running")
        
main()