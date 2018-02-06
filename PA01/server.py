'''
Sample GET Request:
    GET /hello.htm HTTP/1.1
    User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
    Host: www.tutorialspoint.com
    Accept-Language: en-us
    Accept-Encoding: gzip, deflate
    Connection: Keep-Alive

Sample Good response:
    HTTP/1.1 200 OK
    Date: Mon, 27 Jul 2009 12:28:53 GMT
    Server: Apache/2.2.14 (Win32)
    Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT
    Content-Length: 88
    Content-Type: text/html
    Connection: Closed

Sample Bad response:
    HTTP/1.1 404 Not Found
    Date: Sun, 18 Oct 2012 10:36:20 GMT
    Server: Apache/2.2.14 (Win32)
    Content-Length: 230
    Connection: Closed
    Content-Type: text/html; charset=iso-8859-1
'''
import socket
import time
import sys
import signal

# Declare Global variables
serverSocket = None
contentDir='./Uploads'
port=int(sys.argv[1])
form_header = 'HTTP/1.1 {}\nDate: {}\nServer: CS422-Python-Server\nConnection: close \n\n'
html404 = '<html><body><h5>Error 404: File Not Found</h5></body></html>'
html405 = '<html><body><h5>Error 405: Method Not Allowed</h5></body></html>'

def serverStart():
    global serverSocket, port
    # Initialize the socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Quickly restart the server on the same port by using REUSEADDR
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Attempting to launch server on port: {}'.format(port))
    try:
        # Attempt to bind to the port
        serverSocket.bind((socket.gethostname(), port))
    except Exception as e:
        print('Error: unable to obtain port {}\nError: {}'.format(port, e))
        return
    print('Server has started by obtaining port: {}'.format(port))
    listenForConnections()

def listenForConnections():
    while True:
        print('Waiting for a connection')
        # Listen on the socket for a connection and queue at most 5
        serverSocket.listen(5)
        # Accept the connection where clientSocket is the Client's Socket 
        # and addr is the Client's address
        (clientSocket, addr) = serverSocket.accept()
        print('Registered a connection from: {}'.format(addr))
        processRequest(clientSocket, addr)

def processRequest(clientSocket, addr):
    global form_header, html404
    # Try to read the entire content from the socket
    msg = clientSocket.recv(4096)
    # Decode the message from binary to ascii
    str_msg = bytes.decode(msg)
    # Get the tokens from the request
    tokens = str_msg.split(' ')
    # Just accept GET Requests
    if tokens[0] != 'GET':
        # If the method is not GET then send a 405 Method Not Allowed response
        print('{} is not an accepted request method.' \
                '\nGET is the only one accepted'.format(tokens[0]))
        # Send a 405 Response
        sendError(clientSocket, '405 Method Not Allowed', html405)
        return
    elif len(tokens) < 2:
        # Send a 404 Not found response
        sendError(clientSocket, '404 File Not Found', html404)
        return
    # This should be where the file that is requested is called
    req_file = tokens[1]
    # If they just requested root then they probably want index.html
    if req_file == '/':
        req_file = '/index.html'
    # Add the directory to the file
    req_file = contentDir + req_file
    print('Requested File: {}'.format(req_file))
    # Try reading the file and get the data ready to send
    try:
        f = open(req_file, 'rb')
        if tokens[0] == 'GET':
            rep_cont = f.read()
        f.close()
        # Create the headers
        rep_header = form_header.format('200 OK', time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()))
    except Exception as e:
        # Could not find the file so instead send a 404
        print('File Not Found')
        sendError(clientSocket, '404 File Not Found', html404)
        return
    # Encode the header
    server_rep = rep_header.encode()
    # If it is a GET request then add the body data to the response
    if tokens[0] == 'GET':
        server_rep += rep_cont
    # Send the response
    clientSocket.send(server_rep)
    print('Sent and Closing Connection')
    # Close the socket
    clientSocket.close()

# Used for sending Error responses
def sendError(clientSocket, msg, htmlBody):
    rep_header = form_header.format(msg, time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()))
    rep_header = rep_header.encode()
    clientSocket.send(rep_header + htmlBody)
    clientSocket.close()


def sysClear(recSignal, extraParam):
    # Execute this code after catching a control c
    socketClear()
    print('Shutting down the server')
    sys.exit(0)

def socketClear():
    global serverSocket
    try:
        print('\nAttempting to shutdown the socket')
        serverSocket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        print('Could not close the socket\nError: {}'.format(e))

if __name__ == '__main__':
    # Set up a listener for a control c
    signal.signal(signal.SIGINT, sysClear)
    # Start the server
    serverStart()
