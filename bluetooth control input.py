import bluetooth

serverMACAddress = '98:D3:31:FB:50:82'
port = 1
s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
s.connect((serverMACAddress, port))
while 1:
	text = raw_input("input:") 
	if text == "quit":
		break
	s.send(text)
s.close()

