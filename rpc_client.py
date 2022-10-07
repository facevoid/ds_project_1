from copyreg import pickle
from secrets import choice
from urllib import response
from config import config_dict
import socket 
import json 
import os 
from base64 import b64encode
import random 
import numpy as np 
from ast import literal_eval
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

CLIENT_FILE_DIR = config_dict['client_file_dir']

def calculate_pi(s):
    message = json.dumps({"func_name": 'calculate_pi'}).encode()
    s.sendall(message)
    response = s.recv(1024)
    print(f'PI result {response.decode()}')
    if len(response) < 4:
        raise Exception('Lost connection')

def add(s):
    a,b = input('Please enter the two numbers seperated by space\n').split(' ')
    message = json.dumps({"func_name": 'add', 'a': a, 'b': b}).encode()
    s.sendall(message)
    response = s.recv(1048576)
    if len(response) < 2:
        raise Exception('Lost connection')
    

def sort(s):
    array_size = input('Please enter size of the array you want to sort')
    randomlist = random.sample(range(0, 500), int(array_size))
    message = json.dumps({"func_name": 'sort', 'array': randomlist}).encode()
    s.sendall(message)
    response = s.recv(1024)
    if len(response) < 4:
        raise Exception('Lost connection')
    print(f'Sorted Array {response.decode()}')

def matrix_multiply(s):
    matrices = input('Please enter the two tuples seperated by space indicating matrix size (r1,c1) (r2,c2) ').split(' ')
    print(matrices)
    mat_a_shape, mat_b_shape = matrices
    r1, c1 = literal_eval(mat_a_shape)
    r2, c2 = literal_eval(mat_b_shape)
    
    r1 = int(r1)
    c1 = int(c1)
    r2 = int(r2)
    c2 = int(c2)
    
    print(r1, c1, r2, c2)
    mat_a = np.random.rand(r1, c1)
    mat_b = np.random.rand(r2, c2)
    if c1 != r2:
        print('Invalid shape for matrix multiplication')
    
    message = json.dumps({"func_name": 'matrix_multiply', 'mat_a': mat_a, 'mat_b': mat_b}, cls=NumpyEncoder).encode()
    s.sendall(message)
    response = s.recv(1024)
    if len(response) < 4:
        raise Exception('Lost connection')
    print(f'matrix multiplication result {response.decode()}')
    

if __name__ == '__main__':
    function_dict = {1: calculate_pi, 2: add, 3: sort, 4: matrix_multiply}
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((config_dict['host'], config_dict['port']))
        print('Connected to server \n\n')
        while True:
            print('Please select one from the below operations')
            options = {
                1: 'calculate_pi', 2: 'add', 3: 'sort', 4: 'matrix_multiply'
            }
            print(f'{options}')
            selection = int(input('').strip())
            function_dict[selection](s)
            print('Operation Successful')