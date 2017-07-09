import datetime
from   dbHandler import dbHandler
import os
import socket
import subprocess
import sys
import threading
import utilities

HOST = ''
PORT = 8080
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
NUMBEROFTHREADS = 10
CONNECTIONS = {}
DB = dbHandler()

def setupConnection():
    try:
        SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        SOCKET.bind((HOST, PORT))
        SOCKET.listen(NUMBEROFTHREADS)
    except socket.error as errorMsg:
        print(errorMsg)
        setupConnection()

def acceptConnections():
    CONNECTIONS.clear()
    TYPES = {
        '40307': userCommands,
        '90901': adminCommands,
        '80702': govCommands,
        '90201': connectRP
    }
    while True:
        try:
            connection, address = SOCKET.accept()
            connection.setblocking(1)
        except Exception as e:
            print(e)
            continue
        type = str(connection.recv(5))
        thread = threading.Thread(target = TYPES[type] , kwargs={'connection': connection})
        thread.daemon = True
        thread.start()
        print("Connections has been established | IP: " + address[0] + " | Port: " + str(address[1]))

def connectRP(connection):
    handshakePck = str(connection.recv(80))
    print("el handshak "+handshakePck)
    specs = handshakePck.split(':_:')
    DB.addPi(specs[0],specs[1],specs[2],specs[3],specs[4],specs[5])
    mac = specs[1]
    print("El mac eli gayely "+mac)
    CONNECTIONS[mac] = connection

def adminCommands(connection):
    AdminID = str(connection.recv(5)).decode("utf-8")
    cmd = str(connection.recv(2048)).decode("utf-8")
    cmd = cmd.split(":_:")
    if cmd[0] == "15151":
        mac = cmd[1]
        connectionRP = CONNECTIONS[mac]
        connection.send('killer')
        container = cmd[2]
        processNameSize = len(container)
        processNameSize = bin(processNameSize)[2:].zfill(32)
        connection.send(processNameSize)
        connection.send(container)
    if cmd[0] == "27351":
       mac = cmd[1]
       connectionRP = CONNECTIONS[mac]
       print("el mac eli ray7lo "+mac)
       connectionRP.send('shutdw')
       DB.shutPi(AdminID, mac )
    if cmd[0] == "87452":
       mac = cmd[1]
       connectionRP = CONNECTIONS[mac]
       connectionRP.send('restrt')
       DB.restartPi(AdminID, mac )           

def userCommands(connection):
    mac = DB.getBestPi()
    print(mac)
    print("mac is "+mac)

    data = str(connection.recv(1024))
    print("data is "+data)
    path , processName , userID = data.split(":_:")
    print("path "+path + " ,processName "+processName)
    connectionRP = CONNECTIONS[mac]
    connectionRP.send('docker')
    utilities.sendFile(connectionRP, path, processName, userID , 'Dockerfile')
    response = str(connectionRP.recv(11)).decode('utf-8')
    print("el response "+response)
    if response == 'filecreated':
        connectionRP.send('rundocker')
    results = str(connectionRP.recv(1024)).decode('utf-8')
    print("results iare "+results)
    DB.updateResults(userID , processName , results)

# def userCommands(connection):
    # bestPi = dbHandler()
    # mac = bestPi.getBestPi()
    # hostname = CONNECTIONS[mac]
    # specs = str(bestPi.getSpecs(mac)).split(':')
    # username = specs[0]
    # password = specs[1]
    # localPath = str(connection.recv(1024)).decode('utf-8')
    # remotePath = utilities.createPiDir()
    # sftp = utilities.put(hostname, username, password, localPath, remotePath)
    # if sftp:
    #     connection.send(utilities.buildAndRunDocker(hostname, username, password, remotePath))

def govCommands(connection):

    type = str(connection.recv(1)).strip()
    #train the set producing the 2 files
    os.system('cd ~/Desktop/TF_FILES; python train.py')
    print("type is "+type)
    if type == "1":
    # general --> send to all pi-s with camera 
        macs = DB.getCameraPis()
        for x in macs:
            print("el mac "+x)
            connectionRP = CONNECTIONS[x]
            sendToCamera(connectionRP)
        
    if type == "2":
    #specific to pi-s in specific locations    
        locations = str(connection.recv(1024)).strip().split(":_:")
        print(locations)
        macs = DB.getLocatedPis(locations)
        for x in macs:
            connectionRP = CONNECTIONS[x]
            sendToCamera(connectionRP)

    
def sendToCamera(connection):
    directory = "/home/yamen/Desktop/TF_FILES/generated-embeddings"
    connection.send("upload")
    utilities.sendFileCamera(connection , directory , 'classifier.pkl' )
    response = connection.recv(4)

def main():
    setupConnection()
    acceptConnections()

if __name__ == '__main__':
    main()
