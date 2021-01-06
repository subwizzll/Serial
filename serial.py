import math
from os import listdir
import argparse

path = 'C:/Users/Jared/Desktop/VCarvePro/ShopbotApps/Serial/'

numberFiles = listdir(path + 'numbers')

parser = argparse.ArgumentParser(description='Manipulate serial number toolpath parameters')
parser.add_argument('-x','--axisX', type=float, metavar='', required=True, help='Position along X axis to begin cutting.')
parser.add_argument('-y','--axisY', type=float, metavar='', required=True, help='Position along Y axis to begin cutting.')
parser.add_argument('-z','--axisZ', type=float, metavar='', required=True, help='Depth of engraving.')
parser.add_argument('-a','--angle', type=int, metavar='', required=True, help='Angle of engraving')
parser.add_argument('-s','--spacing', type=float, metavar='', required=True, help='Spacing between vectors, 0.1 = 10 percent.')
parser.add_argument('-S','--scaling', type=float, metavar='', required=True, help='Scaling between vectors, 0.1 = 10 percent.')
args = parser.parse_args()

def main():
    data = argsLogRead(path + 'argsLog.log')

    newData = [str(args.axisX),
                str(args.axisY),
                str(args.axisZ),
                str(args.angle),
                str(args.spacing),
                str(args.scaling)]
    
    if newData[0] != data[0]:
        data[0] = newData[0]
        x = float(newData[0])
    else:
        x = float(data[0])
    if newData[1] != data[1]:
        data[1] = newData[1]
        y = float(newData[1])
    else:
        y = float(data[1])
    if newData[2] != data[2]:
        data[2] = newData[2]
        z = float(newData[2])
    else:
        z= float(data[2])
    if newData[3] != data[3]:
        angleStep = int(newData[3]) - int(data[3])
        for file in numberFiles:
            rotateCoordinates(path + 'numbers/' + file, angleStep)
        print(str(data[3]))
        angle = int(newData[3])
    else:
        angle = int(newData[3])
    if newData[4] != data[4]:
        data[4] = newData[4]
        s = float(newData[4]) * 1.1
    else:
        s = float(data[4]) * 1.1
    if newData[5] != data[5]:
        data[5] = newData[5]
        S = float(newData[5]) * 10
    else:
        S = float(data[5]) * 10 


    argsLogWrite(path + 'argsLog.log', newData)

    serial = list(logCount(path + 'MAINPART.LOG').zfill(3))

    code = bytearray(offsetMoveXY(x,y) + fileCall(path,int(serial[0]),S,z,2) + spacing(x,y,S*s,angle) + fileCall(path,int(serial[1]),S,z,2) + spacing(x,y,S*(s*2),angle)+ fileCall(path,int(serial[2]),S,z,2), "utf-8")

    writeSerial(path + 'test.sbp', code)

def argsLogRead(file):
    data = []
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            data.append(line.replace('\n',''))
        f.close()
    return data

def argsLogWrite(file,data):
    with open(file, 'w') as f:
        for i in data:
            f.write(i + '\n')
        f.close()

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

def rotateCoordinates(file, angle):

    with open(file, 'rb+') as f:
        lines = f.readlines()
        newData = []
        for i in lines:
            if i.startswith((b'M3',b'J3')):
                    line = i.split(b',')
                    newXY = rotate((0,0),(float(line[1]),float(line[2])),math.radians(angle))
                    # print(i)
                    newLine = line[0].decode("utf-8")+ ',' + str('%3.6f' % newXY[0]) + ','+ str('%3.6f' % newXY[1]) + ',' + str('%3.6f' % float(line[3]) + '\n')
                    newData.append(bytearray(newLine, 'utf-8'))
            else: newData.append(i)
        f.close()
    
    with open(file, 'wb') as f:
        for i in newData:
            f.write(i)
        f.close()
                
def logCount(file):

    with open(file, 'r') as f:
        x = 0
        logRead = f.readlines()
        for line in logRead:
            if 'File Completed:Yes' in line:
                x += 1

        if x == 0:
            x = 1
        else: x += 1
    return str(x)

def writeSerial(file,i):

    serialFile = open(file,'wb')
    
    i = serialFile.write(i)

    serialFile.close()

def fileCall(path, serial, scaleXY, scaleZ, offset=0, plunge=''):

    # numPath = ['_0.sbp', '_1.sbp', '_2.sbp', '_3.sbp', '_4.sbp', '_5.sbp', '_6.sbp', '_7.sbp', '_8.sbp', '_9.sbp', ]

    prefixString = 'FP,' + path + 'numbers/' + numberFiles[serial]

    fileString = prefixString + ',' + str(scaleXY) + ',' + str(scaleXY) + ',' + str(scaleZ) + ',,' + str(offset) + ',' + plunge + ',0,0\n'

    return fileString

def spacing(ox,oy,s,angle=0):
    if angle > 0:
        values = rotate((0,0),(s,0), math.radians(angle))
        string = 'M2 ' + str('%3.6f' % (ox + values[0])) + ',' + str('%3.6f' % (oy + values[1])) + '\n'
    else:
        string = 'M2 ' + str('%3.6f' % s) + ',' + str('%3.6f' % 0) + '\n'

    return string

def offsetMoveXY(x=0,y=0):
    string = 'M2 ' + str('%3.6f' % x) + ',' + str('%3.6f' % y) + '\n'

    return string

if __name__ == "__main__":
    main()
