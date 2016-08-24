import socket
import xmltodict

from logger import logger


class Client(object):
    buffer = bytearray() # Left-over data from the previous recv

    def __init__(self, client_name, hostname="localhost", port=2323):
        self.client_name = client_name
        self.sock = self.connect(hostname, port)

    def send_actions(self, actions):
        self.send_request(actions)

    def receive_session_end(self):
        resp = self.receive_response(end_tags=['</session-end>'])
        return resp['session-end']

    def receive_turn(self):
        resp = self.receive_response(end_tags=['</turn>', '</round-end>', '</session-end>'])

        if 'turn' in resp:
            return 'turn', resp['turn']
        elif 'round-end' in resp:
            return 'round', resp['round-end']
        else:
            return 'session', resp['session-end']

    def request_round(self):
        req_data = {
            'round-request': None
        }
        self.send_request(req_data)
        return self.receive_round_init()

    def receive_round_init(self):
        resp = self.receive_response(end_tags=['</round-init>'])
        return resp['round-init']

    def request_session(self, inst_name):
        req_data = {
            'session-request': {
                'problem-name': inst_name,
                'client-name': self.client_name,
                'no-header': None
            },
        }
        self.send_request(req_data)
        return self.receive_session_init()

    def receive_session_init(self):
        resp = self.receive_response(end_tags=['</session-init>'])
        return resp['session-init']

    def send_request(self, req_data):
        bin_data = bytearray(xmltodict.unparse(req_data),
                             encoding='utf-8')
        bin_data.append(0)
        self.sock.sendall(bin_data)

    def receive_response(self, end_tags):
        all_data = self.loop_receive(end_tags)
        xmlstr = all_data.decode()
        return xmltodict.parse(xmlstr)

    def loop_receive(self, end_tags):
        all_data = bytearray()

        if len(self.buffer) > 0:
            data = bytes(self.buffer)
        else:
            data = self.sock.recv(4096)

        while data:
            all_data.extend(data)

            for end_tag in end_tags:
                start_index = all_data.find(end_tag)
                if start_index >= 0:
                    end_index = start_index + len(end_tag)
                    self.buffer = bytearray(all_data[end_index:])
                    all_data = all_data[:end_index]
                    return all_data

            data = self.sock.recv(4096)

    def connect(self, hostname, port):
        sock = socket.socket()
        sock.connect((hostname, port))
        logger.info('client_connected')
        return sock

    def disconnect(self):
        logger.info('client_disconnected')
        self.sock.close()
        self.sock = None
