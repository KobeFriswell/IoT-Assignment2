#import pyqrcode
#qr = pyqrcode.create("test1")
#qr.png("test1.png", scale=6)

from PIL import Image
from pyzbar.pyzbar import decode
data = decode(Image.open('C:\\Users\\Desktop\\IoTAssignment2-masterAgentPi\\qrdata\\frame.png'))
print(data[0].data.decode('utf-8'))
