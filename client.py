from secrets import choice
from config import config_dict
import socket 
import json 
import os 
from base64 import b64encode


CLIENT_FILE_DIR = 'client_file_dir'

def upload(s):
    filename = input('Please enter the file name from your directory you want to upload \n')
    # filename = 'hello.txt'#'temp.jpeg'
    filepath = CLIENT_FILE_DIR + '/' + filename
    if os.path.isfile(filepath):
        with open(filepath, 'rb') as fp:
            file_content = b64encode(fp.read())
        message = json.dumps({"choice": 1, 'filename': filename, 'file_content':file_content.decode("utf-8")}).encode()
        s.sendall(message)
    else:
        print('ERROR: file doesn\'t exist')
        return
    data = s.recv(1024)
    if len(data) < 4:
        print(data)
        raise Exception('Lost connection')

def download(s):
    filename = input('Please enter the file name you want to download\n')
    message = json.dumps({"choice": 2, filename: filename}).encode()
    s.sendall(message)
    filecontent = s.recv(1048576)
    if len(filecontent) < 4:
        raise Exception('Lost connection')
    filepath = CLIENT_FILE_DIR + '/' + filename
    with open(filepath, 'wb') as fp:
        fp.write(filecontent) 
    print(f'File {filename} Downloaded successfully')
    

def rename(s):
    filename, new_filename = input('Please enter the file name followed by a space followed by new file name ').split(' ')
    message = json.dumps({"choice": 3, 'filename': filename, 'new_filename': new_filename}).encode()
    s.sendall(message)
    data = s.recv(1024)
    if len(data) < 4:
        raise Exception('Lost connection')
    print(data)

def delete(s):
    filename = input('Please enter the file name you want to delete')
    message = json.dumps({"choice": 4, 'filename': filename}).encode()
    s.sendall(message)
    data = s.recv(1024)
    if len(data) < 4:
        raise Exception('Lost connection')
    print(data) 
    

if __name__ == '__main__':
    function_dict = {1: upload, 2: download, 3: rename, 4: delete}
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((config_dict['host'], config_dict['port']))
        print('Connected to server \n\n')
        while True:
            print('Please select one from the below operations')
            options = {
                1: 'UPLOAD', 2: 'DOWNLOAD', 3: 'RENAME', 4: 'DELETE'
            }
            print(f'{options}')
            selection = int(input('').strip())
            function_dict[selection](s)
            print('Operation Successful')