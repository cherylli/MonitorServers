import socket
import ssl
from datetime import datetime
import pickle

import subprocess
import platform


class Server():
    def __init__(self, name, port, connection, priority):
        self.name = name
        self.port = port
        self.connection = connection.lower()
        self.priority = priority.lower()

        self.history = []
        self.alert = False

    def check_connection(self):
        msg = ""
        success = False
        now = datetime.now()

        try:
            if self.connection == "plain":
                socket.create_connection((self.name, self.port), timeout=10)
            elif self.connection == "ssl":
                ssl.wrap_socket(socket.create_connection(
                    (self.name, self.port), timeout=10))
            else:
                if not self.ping():
                    raise ConnectionError("Cannot reach server with ping.")
            msg = f"{self.name} is up. On port {self.port} with {self.connection}"
            success = True
            self.alert = False
        except socket.timeout:
            msg = f"server: {self.name} is down. On port {self.port}"
        except (ConnectionRefusedError, ConnectionResetError, ConnectionError) as e:
            msg = f"server: {self.name} {e}"
        except Exception as e:
            msg = f"No Clue??: {e}"

        self.create_history(msg, success, now)

    def create_history(self, msg, success, now):
        history_max = 100
        self.history.append((msg, success, now))

        while len(self.history) > history_max:
            self.history.pop(0)

    def ping(self):
        try:
            output = subprocess.check_output(
                f"ping -{'n' if platform.system().lower()=='windows' else 'c'} 1 {self.name}",
                shell=True,
                universal_newlines=True)
            if 'unreachable' in output:
                return False
            else:
                return True
        except Exception:
            return False


if __name__ == "__main__":
    try:
        servers = pickle.load(open("servers.pickle", "rb"))
    except:
        servers = [
            Server("reddit.com", 80, "plain", "high"),
            Server("msn.com", 80, "plain", "high"),
            Server("smtp.gmail.com", 465, "ssl", "high"),
            Server("192.168.1.12", 80, "ping", "high"),
        ]

    for server in servers:
        server.check_connection()
        print(server.history[-1])
        # print(len(server.history))

    pickle.dump(servers, open("servers.pickle", "wb"))
