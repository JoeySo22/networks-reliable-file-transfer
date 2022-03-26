from copy import deepcopy
from socket import AF_INET, SOCK_STREAM, socket
from typing import Dict, List, Tuple

from HelperModule.packet import extract, make, make_empty
from HelperModule.timer import Timer
from HelperModule.udt import recv, send
from SRWindow import SRWindow

class ReliableDataTransferProtocol:

    # sequence number 32 bits (4 byte integer)
    _seq: int = 0
    # base indexx
    _base: int = 0
    # window size
    _win_size: int = 5
    # window
    _window: List[bytes] = []
    # Next Sequence Number
    _next_seq: int = 1
    # Flag for state of sending
    _sending: bytes = False
    # Counter for sending attempts limit
    _sending_tries: int = 5
    # address of this socket
    _addr: Tuple[str, int] = None
    # udp socket for transmitting
    _udp_sock: socket = None
    # save client info
    _client_ip_port: Tuple[str, int] = None
    # helper timer object
    _timer: Timer = Timer(2)

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
        print('recv called')
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
        print('send called')
        if self._protocol == 'gbn':
            self._gbn_send(message)
        if self._protocol == 'sr':
            self._sr_send(message)

    #TODO: Test this
    def _gbn_send(self, message: bytes):
        print('gbn send called.')
        self._sending = True
        while self._sending:
            # Generate window based on message size and send
            self._generate_and_send_window(message)
            # Loop for sending if no correct ACKS received. 
            while self._sending_tries > 0:
                try:
                    # Listen for ACKs and Handle them
                    self._listen_and_handle_acks()
                except:
                    # Resend all of the window
                    self._send_all_window()
                    # Decrement the sending count
                    self._sending_tries -= 1
        
    def _generate_and_send_window(self, message: bytes):
        # Add packets into window win_size number of times. 
        y = (self._win_size - len(self._window))
        for i in range(y):
            # Size of packet must iterate a certain amount
            packet_index: int = self._base * 1020
            # Data to be sent
            data: bytes = message[packet_index: packet_index + 1021]
            # Check if data is small. Its a sign that its the end of the message
            if len(data) < 1020:
                # Set sending flag to false. Done with message. 
                self._sending = False
                # Stop the loop
                break
            # Make packet
            packet: bytes = make(self._seq, data)
            # Make and add packet to window
            self._window.append(make(self._seq, data))
            # Increment the sequence number
            self._seq += 1
            # Send each packet added
            send(packet, self._udp_sock, self._client_ip_port)
            # Debug
            print('sending: seq-' + str(self._seq))

    def _send_all_window(self):
        # Simply send all the packets
        for packet in self._window:
            send(packet, self._udp_sock, self._client_ip_port)

    def _listen_and_handle_acks(self):
        print('listen-and-handle called')
        good_ack_received = False
        while not good_ack_received:
            # Listen to socket
            print('recving packets')
            packet, addr = recv(self._udp_sock)
            # Extract ack num and data
            print('extracting packets')
            ack_num, data = extract(packet)
            # Check if ack number is correct
            if ack_num >= self._base and ack_num < self._next_seq:
                # Pop out everything that has been ACKed
                amount_to_remove = ack_num - self._base + 1
                # Set subset of window as the new window
                self._window = self._window[amount_to_remove:]
                # Flag that an acceptable ACK was received
                good_ack_received = True

    #TODO: test this 
    def _gbn_recv(self, size: int) -> bytes:
        print('gbn recv called')
        message: bytes = b''
        while True:
            # Check if seq received is the next one expected.
            packet, server_addr = recv(self._udp_sock)
            seq_num, data = extract(packet)
            if seq_num is self._seq:
                # Increment sequence
                self._seq += 1
                # If there is data append it to the cumulative message.
                if data:
                    # Add data to send up
                    message = message + data
                # If there is no data, we can end and send message back to app.
                else:
                    break
            send(make(self._seq, make_empty()), self._udp_sock, self._client_ip_port)
            # debug
            print('acking: ack-' + str(self._seq))
        return message

    #TODO: Implement this
    def _sr_send(self, message: bytes):
        self._base = 0
        # Fill up window, send, and start timer
        sr_window = SRWindow(self._win_size)
        for i in range(self._win_size):
            segment = self._base * 1020
            data = message[segment: segment + 1021]
            timer = Timer(3)
            packet = make(self._seq, data)
            sr_window.append(self._seq, packet, timer)
            send(packet, self._udp_sock, self._client_ip_port)
            timer.start()
        # Listen for acks

        pass

    def _sr_fill_window(self, window: SRWindow, packet_num: int, message: bytes) -> bool:
       # Initialize the window with packets 
        while True:
            packet_section = self._base * 1020
            data = message[packet_section:packet_section + 1021]
            timer = Timer(3)
            packet = make(self._seq, data)
            window.append(self._seq, packet, timer)
            send(packet, self._udp_sock, self._client_ip_port)
            self._seq += 1
            self._base += 1
            timer.start()
            if len(packet) < 1025:
                break
            if len(self._window) == self._win_size:
                break
        return len(self._window) 


    #TODO: Implement this
    def _sr_recv(self, num: int) -> bytes:
        pass


    
