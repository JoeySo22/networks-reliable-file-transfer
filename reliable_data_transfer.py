from copy import deepcopy
from curses import window
from email.mime import base
from http import client
from socket import AF_INET, SOCK_STREAM, socket
from typing import Dict, Tuple

from HelperModule.packet import extract, make, make_empty
from HelperModule.timer import Timer
from HelperModule.udt import recv, send

class ReliableDataTransferProtocol:

    # sequence number 32 bits (4 byte integer)
    _seq: int = 0
    # window size
    _win_size = 5
    # address of this socket
    _addr: Tuple[str, int] = None
    # udp socket for transmitting
    _udp_sock: socket = None
    # save client info
    _client_ip_port = None
    # helper timer object
    _timer = Timer(2)

    def __init__(self, sock: socket = socket(AF_INET, SOCK_STREAM), protocol = 'gbn'):
        self._udp_sock = sock
        # Set blocking
        self._udp_sock.settimeout(10)
        # Set protocol
        self._protocol = protocol

    #Binds the socket to a port and domain. 
    def bind(self, ip_port: Tuple[str, int]):
        self._addr = ip_port
        return self._udp_sock.bind(self._addr)

    def listen(self):
        return self._udp_sock.listen()

    def accept(self):
        connection, self._client_ip_port = self._udp_sock.accept()
        connection = ReliableDataTransferProtocol(connection)
        return connection, self._client_ip_port 

    def force_send(self, message):
        return self._udp_sock.send(message)

    def force_recv(self, size: int):
        return self._udp_sock.recv(size)

    def recv(self, bytes_to_read: int) -> bytes:
        if self._protocol == 'gbn':
            return self._gbn_recv(bytes_to_read)
        if self._protocol == 'sr':
            return self._sr_recv(bytes_to_read)
    
    def connect(self, ip_port: Tuple[str, int]):
        return self._udp_sock.connect(ip_port)

    def settimeout(self, seconds: int):
        return self._udp_sock.settimeout(seconds)

    def close(self):
        return self._udp_sock.close()

    def send(self, message: bytes):
        if self._protocol == 'gbn':
            self._gbn_send(message)
        if self._protocol == 'sr':
            self._sr_send(message)

    #TODO: Implement this
    def _gbn_send(self, message: bytes):
        # Set up
        global base
        global window
        global len_mess
        global finished
        base = 0
        window = []
        len_mess = len(message)
        finished = False
        # Method for sending packets
        def send_window_packets(i: int = 0, j: int = self._win_size):
            global window
            print(len(window))
            for p in range(i, j):
                send(window[p], self._udp_sock, self._client_ip_port)
        # Method for filling the sliding window
        def fill_window(slide: int = self._win_size, initial: bool = False, message = message):
            global base
            global window
            global len_mess
            for i in range(slide + 1):
                if not initial:
                    window.pop(0)
                b = window_base_index()
                e = end_index()
                window.append(make(self._seq, message[b: e]))
                self._seq += 1
                base += 1
                if len_mess < e:
                    finished = True
                    break
        # Method for getting byte window base index
        def window_base_index():
            global base
            return base * 1020
        # Method for getting byte end index
        def end_index():
            global base
            return (base + self._win_size) * 1020
        # Fill up initial window
        fill_window(initial=True)
        while not finished:
            # Send all of the packets in the window
            send_window_packets(base, base+self._win_size)
            # Wait for ACKs from the receiver. 
            try:
                data: bytes = recv(self._udp_sock)
                # See what data we received.
                ack_num, data = extract(data)
                if ack_num >= base and ack_num < (base + self._win_size):
                    # update the base and slide the window
                    amount_to_dequeue = ack_num - base + 1
                    fill_window(amount_to_dequeue)
            except socket.timeout:
                # Resend window
                send_window_packets(base, base+self._win_size)

    #TODO: Implement this
    def _gbn_recv(self, size: int) -> bytes:
        delv_mesg = b''
        counter = 0
        time_out_counter = 0
        while True:
            # Receive
            try:
                packet, sender_addr = recv(self._udp_sock)
                # extract ack_num from packet
                ack_num, data = extract(packet)
                # Check if ack number is what we are expecting.
                if ack_num != self._seq:
                    # If not, send the old ack
                    send(make(self._seq, make_empty()), self._udp_sock, sender_addr)
                else:
                    # Send ack
                    send(make(ack_num, make_empty()), self._udp_sock, sender_addr)
                    # Gather to send up
                    delv_mesg = delv_mesg + data
                    # Increment count
                    counter += len(data)
                    # Increase seq num
                    self._seq += 1
                    if counter >= size:
                        break
            except:
                # Try again at least 3 times
                time_out_counter += 1
                if time_out_counter == 3:
                    raise TimeoutError('Timeout expired.')
        return delv_mesg 

    #TODO: Implement this
    def _sr_send(self, message: bytes):
        pass

    #TODO: Implement this
    def _sr_recv(self, num: int) -> bytes:
        pass


    
