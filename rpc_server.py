
from genericpath import isfile
from http import client
import socket
import json 
from ast import literal_eval
from base64 import b64decode
import os 
import traceback
import threading
import pickle 

from config import config_dict
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class Server(object):
    def __init__(self, config_dict) -> None:
        self.host = config_dict['host']
        self.port = config_dict['port']
        self.server_dir = config_dict['server_dir']
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.function_dict = {'calculate_pi': self.calculate_pi, 'add': self.add, 'sort': self.sort, 'matrix_multiply': self.matrix_multiply}
    
    def listen(self):
        self.sock.listen(10)
        while True:
            try:
                client, address = self.sock.accept()
                client.settimeout(60)  #Idle timeout
                threading.Thread(target = self.talk_to_client,args = (client,address)).start()
                
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
                func_name = data['func_name']
                self.function_dict[func_name](client, data)

            except:
                traceback.print_exc()
                print('Client lost the connection ')
                break
        
    def calculate_pi(self, client, data):
        k = 1
        s = 0
        for i in range(1000000):
            if i%2 == 0:
                s += 4/k
            else:
                s -= 4/k
            k+=2
        
        sum_string = str(s)
        client.send(sum_string.encode())
        
    def add(self, client, data):
        a = data['a']
        b = data['b']
        
        client.send(str(int(a) + int(b)).encode())
            
    def sort(self, client, data):
        array = sorted(data['array'])
        result = json.dumps(array)
        client.send(result.encode())
    
    def matrix_multiply(self, client, data):
        mat_a = data['mat_a']
        mat_b = data['mat_b']
        print(type(mat_a), type(mat_b))
        result = np.dot(mat_a, mat_b) 
        client.send(json.dumps(result, cls=NumpyEncoder).encode())
        

if __name__ == '__main__':
    server = Server(config_dict=config_dict)
    server.listen()

#sudo lsof -t -i tcp:8081 | sudo xargs kill