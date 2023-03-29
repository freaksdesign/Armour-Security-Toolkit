import os
import json
import socket
from concurrent.futures import ThreadPoolExecutor



class Scanner:

    def __init__(self, target, port_range, protocol, limit, speed):
        self.target = target
        self.port_list = list(range(*map(int, port_range.split("-")))) + [int(port_range.split("-")[1])]
        self.scan_protocol = protocol
        self.scan_limit = limit
        self.scan_speed = speed
        self.data = []
        self.ports_info = self.load_ports_info()

    def load_ports_info(self):
        with open("./resources/ports.json") as f:
            return json.load(f)

    def is_port_open(self, target, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM if self.scan_protocol == "TCP" else socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.scan_speed)

            try:
                sock.connect((target, port))
                return True
            except:
                return False

    def scan(self):
        with ThreadPoolExecutor(min(len(self.port_list), int(self.scan_limit))) as executor:
            result = executor.map(self.is_port_open, [self.target]*len(self.port_list), self.port_list)

            for port, is_open in zip(self.port_list, result):
                port_data = {
                    "target": self.target,
                    "port": port,
                    "status": "Open" if is_open else "Closed",
                    "service": self.get_port_name(port),
                    "description": self.get_port_description(port)
                }
                self.data.append(port_data)

                if is_open:
                    print(f'Port {port} is open!')

        return self.data

    def get_port_name(self, port):
        try:
            port_name = self.ports_info["data"][str(port)][0]
        except KeyError:
            port_name = "N/A"

        if port_name == "NA":
            port_name = "N/A"

        return port_name

    def get_port_description(self, port):
        try:
            port_description = self.ports_info["data"][str(port)][1]
        except KeyError:
            port_description = "N/A"

        if port_description == "NA":
            port_description = "N/A"

        return port_description
