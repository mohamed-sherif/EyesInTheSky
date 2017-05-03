import socket
import sys
import os
import subprocess
import datetime
import specs

# host = '46.101.180.16'
host = '192.168.8.100'
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def establishConnection():
    try:
        s.connect((host, port))
        s.send('90201')
    except socket.error as errorMsg:
        print(errorMsg)

def createDir():
    directory = '/home/pi/Desktop/' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return directory

def receiveFile(directory):
    try:
        filesize = s.recv(32)
        filesize = int(filesize, 2)
        print('file size '+str(filesize))

        os.mkdir(directory, 0755);
        os.chdir(directory)

        if str(os.getcwd()) == directory:
            f = open('Dockerfile','wb')
            chunksize = 4096

            while filesize > 0:
                if filesize < chunksize:
                    chunksize = filesize
                data = s.recv(chunksize)
                f.write(data)
                filesize -= chunksize
            f.close()
            print 'File received successfully'
    except IOError as e:
        print e

def sendSpecs():
    s.send(specs.StaticSpecs())

def executeCommand():
	sendSpecs()
    while(True):
        if s.recv(6) == 'upload' :
	        directory = createDir()
            receiveFile(directory)
            s.send('filecreated')
            if s.recv(9) == 'rundocker':
                try:
                  	build = 'docker build .'
                 	buildDocker = subprocess.Popen(build, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)
                  	buildOutputBytes = buildDocker.stdout.read() + buildDocker.stderr.read()
                    buildOutput = str.encode(buildOutputBytes)

    		        words = buildOutput.split('Successfully built')
                  	imgID = words[1].strip()

                  	run = 'docker run ' + imgID
                  	runDocker = subprocess.Popen(run, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)
                  	outputBytes = runDocker.stdout.read() + runDocker.stderr.read()
                  	output = str.encode(outputBytes)
                except Exception as e:
              	    output = e
                print(output)
                s.send(output)
    s.close()

def main():
    establishConnection()
    executeCommand()

if __name__ == '__main__':
    main()