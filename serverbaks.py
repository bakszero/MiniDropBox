import sys, os, hashlib
import socket, time
import glob
import re
import subprocess #Using Python3.5.2+
import shlex
import stat
PORT = 1445
HOST = 'localhost'

class server():
    def __init__(self):
        try:
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.serversocket.bind((HOST,PORT))
            self.serversocket.listen(5)
        except socket.error as e:
            print ("Connection refused.")


    def run(self):
        
        while True:
            #Connect with the client, here it creates client sockets.
            try:
                client, addr = self.serversocket.accept()	
                print("Connected with {} :  {}".format(addr[0], str(addr[1])))
                

                #Receive the command from the client
                rec_command = client.recv(1024)
                print ("Client sent >> {}".format(rec_command.decode()))
                print ("Client > ", end = " ", flush = True)

                #Split the received command from the client into lists rather than a string
                rec_command = rec_command.decode().split(" ")

                #Get the current working directory and store it in the 'pwd' variable
                pwd = os.getcwd()
                #Execute the commands
                #This is lls command to get the directories in the server folder
                if (rec_command[0] == "lls"):
                    output = subprocess.check_output(["ls","-l"])
                    #Decode the output into readable format //DOOO NOOOOT DECOOOODEE DURING SEEEND, RATHER ENCODED FORMAT WORKS!!
                    #output = output.decode('utf-8')
                    #send the contents of the output variable to the client on the other side
                    #print output
                    #print (output)
                    client.send(output)
                
                #index <args>
                elif (rec_command[0] == "index"):
                    #index shortlist <arg1> <arg2>
                    if (rec_command[1] == "shortlist"):
                        #Store starttime 
                        starttime = rec_command[2]+' '+rec_command[3]
                        endtime = rec_command[4]+' '+rec_command[5]
                        os.chdir(pwd)
                        #bash_command = "find " + path + " -type f -newermt "+starttime+" ! -newermt "+endtime+" | sed 's/^.\///g'" 
                        #Execute this command
                        temp_output = subprocess.check_output(('find', pwd, '-type', 'f', '-newermt', starttime, '!', '-newermt', endtime))
                        output =temp_output.decode('utf-8').split('\n')
                    # print ("TEMP OUTPUT IS ")
                    # print (output)
                        #print ("OVER")
                    # print (len(output))
                        #IF no match, return blank
                        if len(output)==1:
                            client.send(" ".encode())
                            client.close()
                            return
                            
                        #Declare a resultant resulant string to store final output of all the files that were modified in this time interval
                        result_string=""
                        #After storing the files and directories in the output variable as a list, process the list and send the files to the client
                        for i in output:

                            #VERY VERY IMPORTANT!!! This will reduce double-output!
                            if i is '':
                                break

                            bash_command = subprocess.check_output(['ls -l '+i+' | awk \'{print  $9, $5, $6, $7, $8}\' '],shell=True)
                            decoded_bash_command = bash_command.decode('utf-8')

                            split_command = decoded_bash_command.split(" ")

                            #Get filenames only after slash
                            temp_command = split_command[0].split("/")
                            split_command[0] = temp_command[-1]

                            #Find file type
                            p = subprocess.Popen('file '+i,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell = True)
                            output, errors = p.communicate()
                            output = output.decode().split()[1:]
                            output =" ".join(str(x) for x in output)
                            
                            #print (output)

                            #Convert list to string
                            split_command =" ".join(str(x) for x in split_command)
                            result_string = result_string+ split_command + output
                        #Send the resultant string to the client via the client socket
                        #ALWAYS ENCODE BEFORE SENDING IN PYTHON3
                        result_string=result_string.encode('utf-8')
                        client.send(result_string)
                    
                    #index longlist
                    elif (rec_command[1] == "longlist"):
                        #Redeclare the resultant string
                        result_string=""
                        #Execute command to find all the files
                        temp_output = subprocess.check_output(('find', pwd, '-type', 'f'))
                        output =temp_output.decode('utf-8').split('\n')
                        #Iterate over all the output
                        for i in output:
                            #VERY VERY IMPORTANT!!! This will reduce double-output!
                            if i is '':
                                break
                            #Find the relevant information via awk
                            bash_command = subprocess.check_output(['ls -l '+i+' | awk \'{print $9 ,$5, $6, $7, $8}\' '],shell=True)
                            decoded_bash_command = bash_command.decode('utf-8')
                            #print decoded_bash_command
                            split_command = re.split(" ",decoded_bash_command)

                            #Get filenames only after slash
                            temp_command = split_command[0].split("/")
                            split_command[0] = temp_command[-1]

                            #Convert list to string
                            split_command =" ".join(str(x) for x in split_command)



                            #Find file type
                            p = subprocess.Popen('file '+i,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell = True)
                            output, errors = p.communicate()
                            output = output.decode().split()[1:]
                            output =" ".join(str(x) for x in output)
                            #print (output)

                        # print (split_command)
                            result_string = result_string + split_command + output + "\n"

                        
                            #result = subprocess.check_output(['file',i], shell = True)
                            #result = result.decode()
                            
                            #print (result)
                            
                        #Send the resultant string to the client via the client socket
                        client.send(result_string.encode('utf-8'))
                    
                        client.close()
                    
                    #index regex <arg>
                    elif (rec_command[1] == "regex"):
                        os.chdir(pwd)

                        #Use the regex function to check for matching files
                        matched_files = glob.glob(rec_command[2], recursive = True)
                        #Convert to string and send to the client
                        matched_files =" ".join(str(x) for x in matched_files)
                        client.send(matched_files.encode())

                #hash <args>
                elif (rec_command[0] == "hash"):
                    #hash verify <args>
                    if (rec_command[1] ==  "verify"):
                        if (os.path.isfile(rec_command[2]) is False):
                            client.send("WRONG".encode())
                            print ("File path wrong.")
                            continue
                        #Will consist of hexdigest and timestamp of the file
                        list = []
                        
                        #Attach last modified timestamp
                        list.append(time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(os.path.getmtime(rec_command[2]))))

                        #Compute the hash function now
                        hashfunction = hashlib.md5()
                        with open(rec_command[2], "rb") as file:
                            for chunk in iter(lambda: file.read(4096), b""):
                                hashfunction.update(chunk)
                        #Append hexdigest to the last modified time of the file
                        list.append(hashfunction.hexdigest())
                        #Convert list to string before sending
                        list =" ".join(str(x) for x in list)
                        #Send the list in the form of a string to the client, ENCODED!!!
                        client.send(list.encode())
                        print ("Hashfile generated")
                    
                    #hash checkall 
                    elif (rec_command[1] == "checkall"):
                        #file_list = os.listdir(".")
                        #Execute command to find all the files ONLY! Otherwise upper command yielded directories, and an error persisted.
                        file_list = subprocess.check_output(('find', pwd,  '-type', 'f'))
                        file_list =file_list.decode('utf-8').split('\n')

                        #To delete the final element of the list because it is \n and creates problems later on. Duh!
                        del file_list[-1]
                        #Strip the \n at the end
                        #file_list.strip("\n")
                        #print (file_list)

                        list = []
                        for f in file_list:
                            only_filename = f.split("/")

                            list.append(only_filename[-1])
                            list.append(time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(os.path.getmtime("./serverbaks.py"))))

                            #Compute the hash function now
                            hashfunction = hashlib.md5()
                            #print (f)
                            with open(f, "rb") as file:
                                    for chunk in iter(lambda: file.read(4096), b""):
                                        hashfunction.update(chunk)
                            #Append hexdigest to the last modified time of the file
                            list.append(hashfunction.hexdigest())
                            list.append("\n")
                            #print (list)
                            #End for loop

                        #Convert list to string before sending
                        list =" ".join(str(x) for x in list)
                        #print ("LIST:")
                        #print (list)
                        #Send the list in the form of a string to the client, ENCODED!!!
                        client.send(list.encode())   





                #Now acting if the download command was sent; download <args>
                elif (rec_command[0] == "download"):
                    if (os.path.isfile(rec_command[2]) is False):
                            client.send("WRONG".encode())
                            print ("File path wrong.")
                            continue
                    
                    if (rec_command[1] == "TCP"):
                        #List for the storage of file_data
                        f_list = []
                        #Store the filename
                        
                        
                        filename=rec_command[2]



                    # print (filename)
                        #Open the file
                        f = open(filename,'rb')
                        #Read the first 1024 characters from the file
                        l = f.read(1024)
                        #Loop over the remaining contents
                        while (l):
                            client.send(l)
                            #print('Sent ',repr(l))
                            l = f.read(1024)
                        f.close()

                        print('Done sending')

                    
                    elif (rec_command[1]== "UDP"):

                        #Create the **client** socket connection for UDP transfer
                        server_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        #List for the storage of file_data
                        f_list = []
                        #Store the filename
                        filename=rec_command[2]
                        #print (filename)
                        #Open the file
                        f = open(filename,'rb')
                        #Read the first 32678 characters from the file
                        l = f.read(32678)
                        #Loop over the remaining contents
                        while (l):
                            server_udp_socket.sendto(l, ('localhost', 1403))
                            #print('Sent ',repr(l))
                            l = f.read(32678)
                        f.close()

                        print('UDP Done sending')

                
                elif (rec_command[0] == "downloaddata"):
                    f_list = []
                    #print (rec_command)
                    #Append the filename to the list
                    f_list.append(rec_command[2])
                    #Append the modified time to the list
                    modified_time =(time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(os.path.getmtime(filename))))
                    f_list.append(modified_time)
                    #Compute the hash function now
                    hashfunction = hashlib.md5()
                    with open(rec_command[2], "rb") as file:
                        for chunk in iter(lambda: file.read(4096), b""):
                            hashfunction.update(chunk)
                    #Append hexdigest to the last modified time of the file
                    f_list.append(hashfunction.hexdigest())
                    #Convert list to string before sending
                    f_list =" ".join(str(x) for x in f_list)
                    #Send the list in the form of a string to the client, ENCODED!!!
                    #print ("hhha pks send")
                    client.send(f_list.encode())

                elif (rec_command[0] == "modified"):

                    filename = rec_command[1]
                    last_modified_time = str(os.path.getmtime(filename))

                    client.send(last_modified_time.encode())


                elif (rec_command[0] == "filepermission"):
                    filename = rec_command[1]
                    permission_str = str(os.lstat(filename).st_mode)

                    client.send(permission_str.encode())
                    


                #Close the client
                client.close()
            except socket.error as e:
                print ("Connection refused.")
            
            

Server = server()
Server.run()
Server.serversocket.close()