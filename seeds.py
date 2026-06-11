import socket
import threading
from typing import List
from log import log


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


class Seeds:
    def __init__(self, ip=None, port=0):
        if ip is None:
            self.ip = get_local_ip()
        else:
            self.ip = ip
        self.port = int(port)
        self.server_socket = None
        self.seed_sockets: List[socket.socket] = []
        self.peer_list = []
        self.running_status = True

    def creation(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.ip, self.port))
            if self.port == 0:
                self.port = self.server_socket.getsockname()[1]
            self.server_socket.listen(100)
            msg = f"Seed activated: Listening on {self.ip}:{self.port}"
            print(msg)
            log(msg)
            thread = threading.Thread(target=self.accept_connections, daemon=True)
            thread.start()
            return 1
        except socket.error as e:
            err_msg = f"Failed to activate seed on {self.ip}:{self.port}. Error: {e}"
            print(err_msg)
            return 0

    def accept_connections(self):
        while self.running_status:
            try:
                connection, address = self.server_socket.accept()
                msg = f"Seed({self.ip}:{self.port}) -> New connection from {address[0]}:{address[1]}"
                print(msg)
                log(msg)
                thread = threading.Thread(
                    target=self.handle_peer_connection,
                    args=(connection, address),
                    daemon=True
                )
                thread.start()
            except Exception as e:
                if self.running_status:
                    print(f"Seed({self.ip}:{self.port}) -> Error accepting connection: {e}")
                break

    def handle_peer_connection(self, connection: socket.socket, address):
        # Message handling will be added in the next commit
        pass

    def close(self):
        self.running_status = False
        if self.server_socket:
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            self.server_socket.close()
            msg = f"Seed server on {self.ip}:{self.port} closed."
            print(msg)
            log(msg)
        for conn in self.seed_sockets:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass