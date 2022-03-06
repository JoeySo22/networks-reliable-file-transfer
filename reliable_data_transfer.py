from copy import deepcopy
from socket import AF_INET, SOCK_DGRAM, socket
from typing import Tuple

class ReliableDataTransferProtocol:
    '''
    source port 16 bits(2 bytes size char)
    destination port 16 bits (2 bytes size char)
    sequence number 32 bits (4 byte integer)
    ack number 32 bits (4 byte integer)
    data offset in octets 4 bits(), num of 32-bit words
    reserved bits 3 bits, does nothing. set to 0
    flags 9 bits:
        NS - ECN-nonce concealment protection
        CWR - Congestion window reduced flag set by the sending host that it 
        received a TCP segment with the ECE flag set and had responded in 
        congestion control mechanism. 
        ECE - ECN-Echo has a dual role, depending on the value of the SYN flag. 
        It indicates: if the SYN flag is set(1), the TCP peer is ECN capable. If
        the SYN flag is clear (0), that packet with Congestion Experience flag 
        set (ECN=11) in the IP header was received during normal transmission. 
        This serves as an indication of network congestion (or impending 
        congestion) to the TCP sender. 
        URG - Indicates thet the urgent pointer field is significant.
        ACK - Indicatees that the acknolwedgement field is significant. All 
        packets after the initial SYN packet sent by the cliet should have this
        flag set. 
        PSH - Push function, Asks to push the buffered data to the receiving 
        application. 
        RST - Reset the connection
        SYN - Synchronize sequence numbers. Only the first packet send from each
        end should have this flag set. Some other flags and fields change 
        meaning based on this flag, and some are only valid when it is set, and
        others when it is clear. 
        FIN - The last packet from the sender. 
    Window Size 16 bits, The size of the receive window, which specifies the 
    number of window size units that the sender of this segment is currently 
    willing to receive. 
    Checksum 16 bits
    Urgent pointer 16 bits, If the URG flag is set, then this 16-bit field is an
     offest from the sequence number indicating the last urgent data byte.
    There will be no Options bits.
    '''

    def __init__(self):
        self._udp_sock = socket(AF_INET, SOCK_DGRAM)

    def __init__(self, ip_port: Tuple[str, int]):
        self_udp_sock = socket(AF_INET, SOCK_DGRAM)
        self._addr = deepcopy(ip_port)
        self._udp_sock.bind(ip_port)

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