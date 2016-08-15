import socket
import xmltodict

from logger import logger


class Client(object):

    def __init__(self, client_name, hostname="localhost", port=2323):
        self.client_name = client_name
        self.sock = self.connect(hostname, port)

    def request_session(self, inst_name):
        req_data = {
            'session-request': {
                'problem-name': inst_name,
                'client-name': self.client_name,
                'no-header': None
            },
        }
        bin_data = bytearray(xmltodict.unparse(req_data),
                             encoding='utf-8')
        bin_data.append(0)
        self.sock.sendall(bin_data)
        return self.receive_session_init()

    def receive_session_init(self):
        resp = self.receive_response(end_tag="</session-init>")
        return {
            'session_id': resp['session-id'],
            'num_rounds': resp['num-rounds'],
            'time-allowed': resp['time-allowed'],
        }

    def receive_response(self, end_tag):
        all_data = bytearray()
        data = self.sock.recv(4096)

        while data:
            all_data.extend(data)

            if data[-1] == '\0':
                all_data = all_data[:-1]
                break
            if all_data[-len(end_tag):].decode() == end_tag:
                break

            data = self.sock.recv(4096)

        xmlstr = all_data.decode()
        return xmltodict.parse(xmlstr)

    def connect(self, hostname, port):
        sock = socket.socket()
        sock.connect((hostname, port))
        logger.info('client_connected')
        return sock

    def disconnect(self):
        logger.info('client_disconnected')
        self.sock.close()
        self.sock = None
