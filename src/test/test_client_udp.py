import socket
import sys

HOST, PORT = '184.82.236.126', 9999

# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
while True:
    data = raw_input('new data:')
    sock.sendto(data + "\n", (HOST, PORT))
    received = sock.recv(1024)
    print "Sent:     {}".format(data)
    print "Received: {}".format(received)
