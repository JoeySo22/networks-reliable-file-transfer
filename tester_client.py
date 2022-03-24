from reliable_data_transfer import ReliableDataTransferProtocol

client = ReliableDataTransferProtocol()
client.connect(('localhost', 8888))
print(client.recv(9))