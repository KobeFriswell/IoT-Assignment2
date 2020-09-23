from bluetooth import *
from bluetoothdb import DatabaseUtils

#######################################################
# Scan
#######################################################

target_address = None

nearby_devices = discover_devices(duration=10, flush_cache=True)

MacAddrList=[]
# scanning for target device
for bdaddr in nearby_devices:   
    print('Nearby MacAddr %s'%(bdaddr))
    MacAddrList.append(bdaddr)

Listappend='\',\''.join(MacAddrList)

if Listappend:
    f = DatabaseUtils()
    rows = f.getMacAddress(Listappend)
    cnt=0
    for row in rows:
        print("Find MacAddr ",row[1])
        cnt=1
    if cnt == 0:
        print('No Found MacAddr')
else:
    print('Not Nearby MacAddr')
