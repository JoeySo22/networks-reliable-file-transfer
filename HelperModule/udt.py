# udt.py - Unreliable data transfer using UDP
import random
from socket import socket
from typing import Tuple
DROP_PROB = 2

# Send a packet across the unreliable channel
# Packet may be lost
def send(packet: bytes, sock: socket, addr: Tuple[str, int]) -> None:
    if random.randint(0, 10) > DROP_PROB:
        sock.sendto(packet, addr)
    return

# Receive a packet from the unreliable channel
def recv(sock: socket) -> Tuple[bytes, Tuple[str, int]]:
    packet, addr = sock.recvfrom(1024)
    return packet, addr