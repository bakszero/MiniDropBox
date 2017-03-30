# MiniDropBox
This is a Dropbox-like application level program to keep two separate directories synced using sockets.

A program to keep two separate directories synced, similar to Dropbox, using sockets.

##Basic Info

• The system has 2 clients (acting as servers simultaneously) listening to the communication channel for requests and waiting to share files (avoiding collisions) using an application layer protocol (Here, the files have been named as client and server to differentiate between the two clients).

• Each client has the ability to do the following: – Know the files present on each other's machines in the designated shared folders. – Download files from the other shared folder.

• The system periodically checks for any changes made to the shared folders.

• File transfer incorporates MD5 checksum to handle file transfer errors.

• The history of requests made by either clients is logged at each of the clients respectively.

##Specific Information

A) Manual Mode - Contains a command line interface similar to a shell, to perform the following operations:

###Commands
• index [args]... – Requests the display of the shared files on the connected system. – The flag variable can be:

∗ longlist: Flag would mean that client wants to know the entire listing of the shared directory including ’name’, ’size’, ’timestamp’ and ’type’ of the files. Ex: prompt> index longlist Output: Includes ’name’, ’size’, ’timestamp’ and ’type’ of all the files in the other directory.

∗ shortlist: This flag would mean that the client only wants to know the names of files between a specific set of timestamps. Epoch form of timestamps has been used here. Ex: prompt> index shortlist Output: Includes ’name’, ’size’, ’timestamp’ and ’type’ of the files between the start and end time stamps.

∗ regex: This flag means that the output should be the listing of all files which match the regex. Ex: prompt> index regex .txt$ Output: Details of all files that end with .txt should be displayed.

• hash [args]... – This command indicates that the client wants to check if any of the files on the other end have been changed. – The flag variable can be:

∗ verify: Check for the specific file name provided as command line argument and return its ’checksum’ and ’last modified’ timestamp. Ex: promt> hash verify Output: checksum and last modified timestamp of the input file.

∗ checkall: Performs ’verify’ for all the files in the shared folder. Ex: prompt> hash checkall Output: filename, checksum and last modified timestamp of all the files in the shared directory.

• download [args]... – Used to download files from the shared folder of connected user to our shared folder. The flag variable can take the value TCP or UDP depending on the user’s request. If a socket is not available, it is created and both clients use this socket for file transfer.

Ex: prompt> download TCP Output: Displays the filename, filesize, last modified timestamp and the MD5 hash of the requested file. Also downloads the file and verifys it in case of UDP.

B) Automatic Mode - Provides an automatic file sharing service. The program periodically checks for any updates in the remote folder using the hash values and downloads the remote file, if it is more recent. This is in-built into the application and does not have separate files.
