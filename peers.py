import random
import socket
import threading
from typing import List
import time
from log import log

PING_INTERVAL = 3
PING_MAX_WAIT = 5
GOSSIP_SEND_INTERVAL = 5
NUM_MESSAGES = 10


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


class Peers:
    def __init__(self, ip=None, port=0):
        if ip is None:
            self.ip = get_local_ip()
        else:
            self.ip = ip
        self.port = int(port)
        self.server_socket = None

        self.seed_list = []
        self.peer_list = []
        self.seed_connections: List[socket.socket] = []
        self.peer_connections: List[socket.socket] = []

        self.message_hashes = set()
        self.running_status = True
        self.isDead = False
        self.ping_tracker = {}
        self.peer_info = {}

    def creation(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.ip, self.port))
            if self.port == 0:
                self.port = self.server_socket.getsockname()[1]
            self.server_socket.listen()
            msg = f"Peer listening on {self.ip}:{self.port}"
            print(msg)
            log(msg)
            thread = threading.Thread(target=self.accept_connections, daemon=True)
            thread.start()
        except Exception as e:
            err_msg = f"Error creating peer server on {self.ip}:{self.port}: {e}"
            print(err_msg)

    def connect(self, seeds):
        if len(seeds) > 0:
            self.seed_list = random.sample(seeds, (len(seeds) // 2) + 1)
        for seed in self.seed_list:
            self.connect_to_seed(seed)
        self.request_peer_lists()
        # connect_to_peers and send_connection_update will be added next

    def connect_to_seed(self, seed):
        try:
            seed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            seed_socket.connect((seed[0], seed[1]))
            msg = f"Peer(client)({self.ip}:{self.port}) -> Connected to seed {seed[0]}:{seed[1]}"
            print(msg)
            log(msg)
            seed_socket.sendall(f"PEER_SERVER:{self.port}\n".encode('utf-8'))
            self.seed_connections.append(seed_socket)
        except socket.error as e:
            err_msg = f"Peer(client)({self.ip}:{self.port}) -> Failed to connect to seed {seed[0]}:{seed[1]}. Error: {e}"
            print(err_msg)

    def request_peer_lists(self):
        merged_peers = {}
        for seed_socket in self.seed_connections:
            try:
                seed_socket.sendall(f"REQUEST_PEER_LIST:{self.port}\n".encode('utf-8'))
                peer_list_str = seed_socket.recv(1024).decode('utf-8')
                if peer_list_str:
                    for peer in peer_list_str.split('\n'):
                        if peer:
                            parts = peer.split(':')
                            if len(parts) != 3:
                                continue
                            ip, port_str, degree_str = parts
                            try:
                                port = int(port_str)
                                degree = int(degree_str)
                            except ValueError:
                                continue
                            key = (ip, port)
                            if key in merged_peers:
                                merged_peers[key] = max(merged_peers[key], degree)
                            else:
                                merged_peers[key] = degree
            except Exception as e:
                err_msg = f"Peer(client)({self.ip}:{self.port}) -> Error requesting peer list: {e}"
                print(err_msg)
        self.peer_list = [(ip, port, merged_peers[(ip, port)]) for (ip, port) in merged_peers]
        msg = f"Peer(client)({self.ip}:{self.port}) -> Merged peer list: {self.peer_list}"
        print(msg)
        log(msg)

    def accept_connections(self):
        # Placeholder — full listener added in next commit
        while self.running_status and not self.isDead:
            try:
                connection, address = self.server_socket.accept()
                msg = f"Peer(server)({self.ip}:{self.port}) -> New connection from {address[0]}:{address[1]}"
                print(msg)
                log(msg)
                self.peer_connections.append(connection)
            except Exception as e:
                if self.running_status:
                    print(f"Peer(server)({self.ip}:{self.port}) -> Error accepting: {e}")
                break

    def close(self):
        self.running_status = False
        if self.server_socket:
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            self.server_socket.close()
            msg = f"Peer on {self.ip}:{self.port} closed."
            print(msg)
            log(msg)


            

def connect(self, seeds):
        if len(seeds) > 0:
            self.seed_list = random.sample(seeds, (len(seeds) // 2) + 1)
        for seed in self.seed_list:
            self.connect_to_seed(seed)
        self.request_peer_lists()
        self.connect_to_peers()
        self.send_connection_update()

def connect_to_peers(self):
    for peer in set(self.peer_list):
        peer_ip, peer_port, peer_degree = peer
        if peer_ip == self.ip and peer_port == self.port:
            continue
        threshold = 1 / (peer_degree + 1)
        rand_val = random.random()
        msg = f"Evaluating {peer_ip}:{peer_port} degree={peer_degree} threshold={threshold:.4f} rand={rand_val:.4f}"
        print(msg)
        log(msg)
        if len(self.peer_list) == 1:
            threshold = 0
        if rand_val > threshold:
            try:
                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_socket.connect((peer_ip, peer_port))
                self.peer_connections.append(peer_socket)
                peer_socket.sendall(f"NEW_PEER_SERVER:{self.port}\n".encode('utf-8'))
                self.peer_info[peer_socket] = (peer_ip, peer_port)
                msg = f"Peer(client)({self.ip}:{self.port}) -> Connected to peer {peer_ip}:{peer_port}"
                print(msg)
                log(msg)
                thread = threading.Thread(
                    target=self.peer_listener,
                    args=(peer_socket, "", False),
                    daemon=True
                )
                thread.start()
            except socket.error as e:
                print(f"Peer(client)({self.ip}:{self.port}) -> Failed to connect to {peer_ip}:{peer_port}. Error: {e}")

def send_connection_update(self):
    connected_peers = []
    for peer_socket in self.peer_connections:
        try:
            peer_addr = peer_socket.getpeername()
            connected_peers.append(f"{peer_addr[0]}:{peer_addr[1]}")
        except Exception:
            continue
    new_degree = len(self.peer_connections)
    update_msg = f"CONNECTION_UPDATE:{self.ip}:{self.port}:{new_degree}:"
    if connected_peers:
        update_msg += ",".join(connected_peers)
    update_msg += "\n"
    for seed_socket in self.seed_connections:
        try:
            seed_socket.sendall(update_msg.encode('utf-8'))
            msg = f"Peer(client)({self.ip}:{self.port}) -> Sent connection update to seed"
            print(msg)
            log(msg)
        except Exception as e:
            print(f"Peer(client)({self.ip}:{self.port}) -> Failed to send connection update: {e}")