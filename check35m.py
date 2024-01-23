from socket import *
from datetime import datetime
import time

messout = b"all"

while True :
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.sendto(messout, ('10.75.0.152', 6251))
    messin, server = sock.recvfrom(1024)
    sock.close()
    messin=messin.decode()

    # strip off beginning.
    # replace = with =', and replace space with space'
    # for example dewPoint=14.0 becomes dewPoint='14.0'
    start = messin.find('timeStamp')
    stop = messin.find('end')
    stuff = messin[start:stop].replace ("=","='").replace (" ","'; ")
    print(stuff)

    # exec - causes the pieces to become global variables
    exec(stuff)

    try:
        encl35m
    except NameError:
        encl35m = "-1"

    if ( encl35m == "-1" ) :
      stat35m="unknown"
    elif ( encl35m == "open" ) :
      stat35m="open"
    else:
      stat35m="closed"


    try:
        encl25m
    except NameError:
        encl25m = "-1"
    if ( encl25m == "-1" ) :
      stat25m="unknown"
    elif ( encl25m == "16" ) :
      stat25m="open"
    else:
      stat25m="closed"

    now=datetime.now()
    print("Enclosure: 3.5m",stat35m,", 2.5m",stat25m, "at",now.strftime("%d/%m/%Y %H:%M:%S"))

    time.sleep(10)
