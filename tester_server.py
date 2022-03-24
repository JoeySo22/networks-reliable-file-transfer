from reliable_data_transfer import ReliableDataTransferProtocol

server = ReliableDataTransferProtocol()

server.bind(('localhost', 8888))
server.listen()
connection, client_addr = server.accept()
try:
    connection.send(b'this text')
except Exception as e:
    print(e)
    server.close()


