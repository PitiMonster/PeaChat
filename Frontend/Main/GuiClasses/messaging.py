import time
from threading import Thread
import json
import websocket
import zmq
from PyQt5 import QtCore
from vexmessage import create_vex_message, decode_vex_message



class Messenger(QtCore.QObject):
    message_signal = QtCore.pyqtSignal()
    key_received_signal = QtCore.pyqtSignal()
    request_received_singal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        websocket.enableTrace(True)
        self.callback_new_message_reveiced = []
        self.callback_new_key_request = []
        self.callback_new_key_response = []
        self.callback_new_friend_request = []

    def add_callback_new_message_received(self, f):
        self.callback_new_message_reveiced.append(f)
    
    def add_callback_new_key_request(self, f):
        self.callback_new_key_request.append(f)

    def add_callback_new_key_response(self, f):
        self.callback_new_key_response.append(f)

    def add_callback_new_friend_request(self, f):
        self.callback_new_friend_request.append(f)

    def on_message(self, data):
        data = json.loads(data)
        if(data['type'] == 'new_message'):
            for f in self.callback_new_message_reveiced:
                f(data)
            self.message_signal.emit()
        elif(data['type'] == 'key_request'):
            for f in self.callback_new_key_request:
                f(data)
        elif(data['type'] == 'key_response'):
            for f in self.callback_new_key_response:
                f(data)
            self.key_received_signal.emit()
        elif data['type'] == 'friend_request':
            for f in self.callback_new_friend_request:
                f(data)
            self.request_received_singal.emit()

    def on_error(self, *args):
        print('Errors:')
        print(args)

    def on_close(self):
        print("### closed ###")

    def subscribe_to_socket(self, address: str, token: str):
        headers = {'Authorization': 'Token ' + token}

        self.sub_socket = websocket.WebSocketApp(address,
                        header=headers,
                        on_message = self.on_message,
                        on_error = self.on_error,
                        on_close = self.on_close)

        self.thread = Thread(target=self.sub_socket.run_forever, daemon=True)
        self.thread.start()

    def send_friend_request(self, username):
        data = {
            'type': 'invite_friend',
            'friend': username
        }
        self.sub_socket.send(json.dumps(data))

    def publish_message(self, message, conversation_id):
        data = {
                'type': 'message',
                'content': message,
                'conversation_id': conversation_id
            }
        self.sub_socket.send(json.dumps(data))

    def send_key_request(self, conversation_id, dh_key):
        data = {
                'type': 'key_request',
                'conversation_id': conversation_id,
                'dh_key': dh_key
            }
        self.sub_socket.send(json.dumps(data))

    def send_key_response(self, conversation_id, user_id, dh_key, rsa_key):
        data = {
                'type': 'key_response',
                'conversation_id': conversation_id,
                'user_id': user_id,
                'dh_key': dh_key,
                'rsa_key': rsa_key
            }
        self.sub_socket.send(json.dumps(data))
