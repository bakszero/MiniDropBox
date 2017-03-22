import sys, os, hashlib
import socket, time
import glob
import re
import subprocess #Using Python3.5.2+
import random
from datetime import datetime
import select
import cmd

# python startup file 
import readline 
import rlcompleter 
import atexit 
import os
# tab completion 
readline.parse_and_bind('tab: complete') 
# history file 
histfile = os.path.join(os.environ['HOME'], '.pythonhistory') 
try: 
    readline.read_history_file(histfile) 
except IOError: 
    pass 
atexit.register(readline.write_history_file, histfile) 
del  histfile, readline, rlcompleter


HOST = 'localhost'   #server name goes in here
PORT = 1443

class client:
    def __init__ (self):
        self.init_time = datetime.now()
        

    def download(self, input_command, file_str):
        if (input_command[1] == "TCP"):
            #Create a new client socket for connections with the server.
            try:
                cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cli_socket.connect((HOST, PORT))
            except socket.error as e:
                print ("Connection refused.")

            #Open a new file received_file and receive all the data in that file
            
            with open(file_str, 'wb') as f:
                    print ('A new creative file opened')
                    #Convert to string and send to the server
                    input_temp_command =" ".join(str(x) for x in input_command)
                    cli_socket.send(input_temp_command.encode('utf-8'))

            
                    while True:
                        
                        data = cli_socket.recv(1024)
                        if (data.decode() == 'WRONG'):
                            print ("Wrong file. Enter the correct file")
                            return
                        #print("data={}".format(data))
                        print('receiving data...')
                        if not data:
                            break
                        # write data to a file
                        f.write(data)

            f.close()

            #Set file permissions. BONUS!

            str_filep = self.get_file_permission(["filepermission", input_command[2]])
            print (str_filep)
            int_filep = int(str_filep)
            print (file_str)
            print (int_filep)
            try:
                os.chmod(file_str,int_filep)
                print ("Set file permissions of {} to {}".format(file_str, oct(int_filep)))
            except:
                print ("You do not have sufficient read permissions to access the last modified file")

            

            
            print('Successfully got the file')
            
            cli_socket.close()

            #Create a new socket function for receiving this data
            try:
                cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cli_socket.connect((HOST, PORT))
            except socket.error as e:
                print ("Connection refused.")

            #Concatening the string
            str_data = "downloaddata TCP "
            b = input_command[2]
            str_data = str_data + b
            cli_socket.send(str_data.encode())
            #Now printing the received file data
            file_data = cli_socket.recv(1024)
            #print (file_data)
            #Decode!
            file_data =file_data.decode()
            #Convert the decoded string back to a list for easy access to data
            #file_data = file_data.split(" ")
            print (file_data)
            #f.close()
            cli_socket.close()

        elif (input_command[1] == "UDP"):
            #Create a new client socket(original TCP acting as client) for connections with the server.
            try:
                cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cli_socket.connect((HOST, PORT))
            except socket.error as e:
                print ("Connection refused.")

            #Create a new UDP client socket server for connections with the original server.
            cli_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            UDP_HOST = 'localhost'
            UDP_PORT = 1401
            cli_udp_socket.bind((UDP_HOST, UDP_PORT))
            #Set time-out on the UDP socket.
            cli_udp_socket.settimeout(30)

            #cli_socket.connect((HOST, PORT))
            
            
            
            #Open a new file received_file and receive all the data in that file
            with open('udp_received_file', 'wb') as fudp:
                    print ('file opened')
                    #Convert to string and send to the server
                    input_temp_command =" ".join(str(x) for x in input_command)
                    cli_socket.send(input_temp_command.encode('utf-8'))

            
                    while True:
                        print('receiving data...')
                        try:
                            data, addr = cli_udp_socket.recvfrom(32678)
                        except socket.timeout:
                            print("Write timeout on socket")
                            break
                        #print (data)
                        print (addr)
                        fudp.write(data)
                        
                        if (data == ''):
                            break
                        #print("data={}".format(data))
                        if not data:
                            break
                        # write data to a file
                        

            #f.close()
            print('Successfully got the UDP file....Verifying now..')
            
            cli_socket.close()

            #----------------------------------------------------------------------
            #Verify the calculated hash with the received file hash
            #Create a new socket function for receiving this data
            try:
                cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cli_socket.connect((HOST, PORT))
            except socket.error as e:
                print ("Connection refused.")

            #Concatening the string
            str_data = "downloaddata TCP "
            b = input_command[2]
            str_data = str_data + b
            cli_socket.send(str_data.encode())
            #Now printing the received file data
            file_data = cli_socket.recv(1024)
            #print (file_data)
            #Decode!
            file_data =file_data.decode()

            
            print (file_data)

            #Convert the decoded string back to a list for easy access to data
            file_data = file_data.split(" ")
            #Store the UDP hash somewhere, it is the last member of the file_data list
            udp_hash = file_data[-1]
            #TIME TO CALCULATE THE HASH OF THIS FILE 
            #Compute the hash function now
            hashfunction = hashlib.md5()
            with open("udp_received_file", "rb") as file:
                for chunk in iter(lambda: file.read(4096), b""):
                    hashfunction.update(chunk)
            #Append hexdigest to the last modified time of the file
            udp_thishash= hashfunction.hexdigest()

            print ("This file's hash here is {}".format(udp_thishash))
            if(udp_hash == udp_thishash):
                print ("YES! LUCKY! SUCCESSFUL UDP TRANSFER")
            else:
                print("Sadly your UDP was Unethical Destructive Protocol")
            #f.close()
            cli_socket.close()
            



    def hash(self, input_command):
        #Create a new client socket for connections with the server.
        try:
            cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cli_socket.connect((HOST, PORT))
        except socket.error as e:
            print ("Connection refused.")

        if (input_command[1] == "verify"):
            #Store the filename in a variable, can be used later
            filename = input_command[2]
            
            #Convert to string and send to the server
            input_command =" ".join(str(x) for x in input_command)
            cli_socket.send(input_command.encode('utf-8'))

            #Receive the output of the command from the other client i.e. the server in our case    
            cli_output = cli_socket.recv(1024)
            if (cli_output.decode() == 'WRONG'):
                print ("Wrong file. Enter the correct file")
                return
            #Decode!
            cli_output = cli_output.decode()
            #Convert the decoded string back to a string for easy access to data
            cli_output =cli_output.split(" ")
            #print (cli_output)
            print ("The hash of the file {} is {} , last modified on {} {} {}.".format(filename,cli_output[3] ,cli_output[0], cli_output[1], cli_output[2]))
            return cli_output
            cli_socket.close()

        elif (input_command[1] == "checkall"):
            #Convert to string and send to the server
            input_command =" ".join(str(x) for x in input_command)
            cli_socket.send(input_command.encode('utf-8'))

            #Receive the output of the command from the other client i.e. the server in our case    
            cli_output = cli_socket.recv(1024)
            #Decode!
            cli_output = cli_output.decode()
            #Convert the decoded string back to a string for easy access to data
            cli_output =cli_output.split("\n")

            print ("Filenames with their last modified times and their hashes: \n")
            for i in cli_output:
                print (i)
            return cli_output
            cli_socket.close()





    def index(self, input_command):
        #Create a new client socket for connections with the server.
        try:
            cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cli_socket.connect((HOST, PORT))
        except socket.error as e:
            print ("Connection refused.")
        #Convert to string and send to the server
        input_command =" ".join(str(x) for x in input_command)
        cli_socket.send(input_command.encode('utf-8'))

        #Receive the command's output when it was run on the server/the other client.
        cli_output = ""
        cli_output = cli_socket.recv(1024)

        cli_output = cli_output.decode()
        list_cli_output = cli_output.split(" ")
        #for i in cli_output:
        #print (len(list_cli_output))

        if (len(list_cli_output) == 0):
            cli_socket.close()
            return
        print (cli_output)
        #print (cli_output)

        cli_socket.close()
        return



    def getlist(self, input_command):
        #Create a new client socket for connections with the server.
        try:
            cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cli_socket.connect((HOST, PORT))
        except socket.error as e:
            print ("Connection refused.")
        #Convert input_command into a string for send, since send does not accept lists.
        input_command =" ".join(str(x) for x in input_command)
        #Send the string via the socket to the server.
        #print (type(input_command))
        cli_socket.send((input_command).encode('utf-8'))

        #Receive the command's output when it was run on the server/the other client.
        cli_output = cli_socket.recv(1024)
        print (cli_output.decode())

        cli_socket.close()

        cli_output =  cli_output.decode().split("\n")
        
        #Remove total 140
        del cli_output[0]
        #Remove last element which is nothing basically
        del cli_output[-1]
        
        return cli_output
    
    def get_file_permission(self, input_command):
        #Create a new client socket for connections with the server.
        try:
            cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cli_socket.connect((HOST, PORT))
        except socket.error as e:
            print ("Connection refused.")
        #Convert input_command into a string for send, since send does not accept lists.
        input_command =" ".join(str(x) for x in input_command)
        #Send the string via the socket to the server.
        #print (type(input_command))
        cli_socket.send((input_command).encode('utf-8'))

        #Receive the command's output when it was run on the server/the other client.
        cli_output = cli_socket.recv(1024)
        print (cli_output.decode())
        return (cli_output.decode())
        cli_socket.close()


    def get_last_modified_time(self, input_command):
        #Create a new client socket for connections with the server.
        try:
            cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cli_socket.connect((HOST, PORT))
        except socket.error as e:
            print ("Connection refused.")
        #Convert input_command into a string for send, since send does not accept lists.
        input_command =" ".join(str(x) for x in input_command)
        #Send the string via the socket to the server.
        #print (type(input_command))
        cli_socket.send((input_command).encode('utf-8'))

        #Receive the command's output when it was run on the server/the other client.
        cli_output = cli_socket.recv(1024)
        print (cli_output.decode())
        return (cli_output.decode())
        cli_socket.close()

    def sync(self):
        
        #Periodically check if files are present or not first
        #print ("HI")
        #Check for files in the current directory
        local_file_list = os.listdir(".")
        print (local_file_list)
        
        #Get files from those directory
        get_list = ["lls"]
        lls_list = self.getlist(get_list)
        temp_list= []

        #Store filenames in server_file_list
        server_file_list=[]
        for element in lls_list:
            temp_list = element.split(" ")
            server_file_list.append(temp_list[-1])
        #Iterate over the elements
        for element in server_file_list:
            if element is '':
                break
            if element is None:
                break
            if element in local_file_list:
                continue
            self.download(["download", "TCP", element], element)
            print ("Successfully download file {}".format(element))
        print (server_file_list)


        #Get the local file list again for hash verification with the server
        local_file_list = os.listdir(".")

        for element in server_file_list:
            if element is None:
                continue
            hash_server_list = self.hash(["hash", "verify", element])
            hash_server_file = hash_server_list[3]

            #Compute the hash function now for local file
            hashfunction = hashlib.md5()
            with open(element, "rb") as file:
                for chunk in iter(lambda: file.read(4096), b""):
                    hashfunction.update(chunk)
            #Append hexdigest to the last modified time of the file
            hash_local_file = hashfunction.hexdigest()

            server_last_modified = self.get_last_modified_time(["modified", element])
            client_last_modified = str(os.path.getmtime(element))
            if (client_last_modified > server_last_modified):
                continue
            else:
                if(hash_local_file != hash_server_file):
                    self.download(["download", "TCP", element], element)
                    #print ("Holaa")
        
        return



        #for f in file_list:
            



    def run(self):
        #Main Loop
        
        while True:
            
            #The left-most symbol in the application
            print ('Client > ', end = " ", flush= True)

            #Time-out for automatic sync
            i, o, e = select.select( [sys.stdin], [], [], 100)

            if (i):
                input_command =  sys.stdin.readline().strip()
                #Read in the input command, stripped of whitespaces at the back and the end
                #input_command = input().strip()
                #Transform the string into a list to better capture the 
                input_command = input_command.split(" ")
                #print len(input_command)


                if (len(input_command) == 1):
                    #ls command output handling
                    if(input_command[0] == "ls"):
                        file_list = os.listdir(".")
                        for f in file_list:
                            print (f)

                    #lls is the long-list output from the server directory
                    elif (input_command[0] == "lls" ):
                        lls_list = self.getlist(input_command)
                        #print (lls_list)
                    
                    #RUN THE SYNC COMMAND!
                    elif (input_command[0] == "sync"):
                        self.sync()
                
                #index functions
                elif (input_command[0] == "index"):
                    self.index(input_command)

                #hash functions
                elif (input_command[0] == "hash"):
                    cli_hash_list = self.hash(input_command)
                    #print (cli_hash_list)
                    #print (cli_hash_list)

                #download function call
                elif (input_command[0] == "download"):
                    name_of_file = 'received_file_'
                    random_int = str(random.randrange(1,1000))
                    name_of_file = name_of_file + random_int
                    self.download(input_command, name_of_file)
                    #print (type(input_command))
                else:
                    print ("Please enter a valid command.")
            else:
               # os.system("clear")
                self.sync()
                os.system("clear")




Client = client()
Client.run()
