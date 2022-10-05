
from genericpath import isfile
from http import client
import socket
import json 
from ast import literal_eval
from base64 import b64decode
import os 
import traceback

from config import config_dict

class Server(object):
    def __init__(self, config_dict) -> None:
        self.host = config_dict['host']
        self.port = config_dict['port']
        self.server_dir = config_dict['server_dir']
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.function_dict = {1: self.upload, 2: self.download, 3: self.rename, 4: self.delete}
    
    def listen(self):
        self.sock.listen(1)
        while True:
            try:
                client, address = self.sock.accept()
                client.settimeout(60)  #Idle timeout
                self.talk_to_client(client=client, address=address)
            except:
                raise Exception('Server stopped')
    
    def talk_to_client(self, client, address):
        size = 1048576
        while True:
            try:
                data = client.recv(size).decode('utf-8')
                if len(data) < 10:
                    continue
                data = literal_eval(data)
                choice = data['choice']
                self.function_dict[choice](client, data)
                
            except:
                traceback.print_exc()
                print('Client lost the connection ')
                break
            
    def perform_operations(self, client, data):
        self.function_dict[data['choice']](client, data)
        
    def upload(self, client, data):
        filename = data['filename']
        file_content = b64decode(data['file_content'])
        with open(self.server_dir + '/' + filename, 'wb') as fp:
            fp.write(file_content)
        client.send(b'File Uploaded successfully')
        
    def download(self, client, data):
        filename = data['filename']
        file_content = data['file_content']
        with open(self.server_dir + '/' + filename, 'rb') as fp:
            file_content = fp.read()
            client.send(file_content.encode('utf-8'))
            
    def rename(self, client, data):
        old_file = os.path.join(self.server_dir, data['filename'])
        new_file = os.path.join(self.server_dir, data['new_filename'])
        if os.path.isfile(old_file):
            os.rename(old_file, new_file)
            client.send(b'File renamed successfully')
        else:
            client.send(b'File doesn\'t exist')
    
    def delete(self, client, data):
        file = os.path.join(self.server_dir, data['filename']) 
        if os.path.isfile(file):
            os.remove(file)
            client.send(b'File has been deleted')
        else:
            client.send(b'File doesn\'t exist')

if __name__ == '__main__':
    server = Server(config_dict=config_dict)
    server.listen()

#sudo lsof -t -i tcp:8081 | sudo xargs kill