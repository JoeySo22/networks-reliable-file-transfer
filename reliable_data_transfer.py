from copy import deepcopy
from socket import AF_INET, SOCK_DGRAM, socket
from typing import Tuple

class ReliableDataTransferProtocol:
    '''
    sequence number 32 bits (4 byte integer)
    '''

    def __init__(self):
        self._udp_sock = socket(AF_INET, SOCK_DGRAM)
        self._s_port: int = 0
        self._d_port: int = 0
        self._seq: int = 0


    def __init__(self, ip_port: Tuple[str, int]):
        self_udp_sock = socket(AF_INET, SOCK_DGRAM)
        self._addr = deepcopy(ip_port)
        self._udp_sock.bind(ip_port)
        self._s_port: int = 0
        self._d_port: int = 0
        self._seq: int = 0

    '''Need methods that produces and consumes RDT header data.'''
    @classmethod
    def __encode(cls, i: int, fill: int) -> bytes:
        return str(i).zfill(fill).encode()

    def _produce_header(self, data: bytes):
        '''I won't be implementing bit size headers as its done in TCP but 
        rather implement it with just utf encoding instead.'''
        return self.__encode(self._s_port, 5) \
            + self.__encode(self._d_port, 5) \
            + self.__encode(self._seq, 10) + data 

    def _consumer_header(self, data: bytes):
        self._seq 
        pass

    ''' Wrapper functions so clients & servers don't have to know the 
    difference'''

    #Binds the socket to a port and domain. 
    def bind(self, ip_port: Tuple[str, int]):
        self._addr = ip_port
        return self._udp_sock.bind(self._addr)

    def listen(self):
        '''I don't know exactly what this method does except the limit of 
        connections it can have at a time. Right now I don't need to enfore that. 
        '''
        return


    '''
    This function is special to be implemented. It is supposed to do a hand-shake
    and return a socket and the address. UDP is connectionless.'''
    def accept(self):
        '''Returns a tuple of a socket (this class) and an address.'''
        addr_copy = deepcopy(self._addr)
        return ReliableDataTransferProtocol(), (addr_copy) # (ip:str , port: int)

    #TODO: Implement this
    def recv(self, bytes_to_read: int)):
        pass

    def sendall(self, message: str):
        return self.sendall(message.encode())
    
    #TODO: implement
    def sendall(self, message: bytes):
        pass

    #TODO: implement
    def connect(self, ip_port: Tuple[str, int]):
        pass

    def settimeout(self, seconds: int):
        return self._udp_sock.settimeout(seconds)

    #TODO: implement
    def close(self):
        return self._udp_sock.close()

    def send(self, message: str):
        return self.send(self, message.encode())

    #TODO: implement
    def send(self, message: bytes):
        pass

    
