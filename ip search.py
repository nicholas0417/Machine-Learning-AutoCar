import socket
#-------------------------PC IP-----------------------
hostname = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
hostname.connect(("192.168.0.1", 80))
LocalIP = hostname.getsockname()[0]
hostname.close()
print(LocalIP)
name1 = "tom-rpi"
print socket.gethostbyname(name1)
#----------------------------rpi IP-------------------
name = "tom-rpi"
print socket.gethostbyname(name)

name1 = "project-rpi"
print socket.gethostbyname(name1)
#----------------------------rpi IP-------------------





