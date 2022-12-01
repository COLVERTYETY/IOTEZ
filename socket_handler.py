import socket
import time
import sys
import os
import json
import pandas as pd
import numpy as np
from queue import Queue
from settings import *
import threading

class threadSafeDict(dict):
    def __init__(self):
        self.lock = threading.Lock()
        super().__init__()
    def __setitem__(self, key, value):
        with self.lock:
            super().__setitem__(key, value)
    def __getitem__(self, key):
        with self.lock:
            return super().__getitem__(key)


class SocketActor:
    def __init__(self, buffer_size=1, Queue_Size=1000):
        self.buffer_size = buffer_size
        self.host = IP
        self.port = PORT_SOCKET
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # add this line to fix the error: OSError: [Errno 98] Address already in use
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        self.Q_size = Queue_Size
        self.data  = Queue(maxsize=self.Q_size)
        self.connection_records = threadSafeDict()
    
    def run(self):
        # multithraded server
        while True:
            client, address = self.socket.accept()
            #  start the thread
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        client.settimeout(3)
        cumul = ""
        print(f"Listening to {address}")
        self.connection_records[address] = "connected"
        #  while client has not timed out
        while True:
            try:
                #  with a time out of 2 seconds
                data = client.recv(self.buffer_size)
                # print(data.decode("utf-8"))
                if data and len(data)>0:
                    cumul = self.decode(data.decode("utf-8"), cumul, address)
                    #  set the last time the client was active
                else:
                    raise Exception('Client Timed Out')
            except Exception as e:
                self.connection_records[address] = "disconnected"
                print(f"Client {address} disconnected", e)
                client.close()
                return False

    def status(self):
        #  retiurn a json of the connection records
        myjspn = "{"
        for key, value in self.connection_records.items():
            myjspn+=f"{key}: {value},"
        myjspn+="}"
        return myjspn

    def __repr__(self):
        buffer = f"Number of connections: {len(self.connection_records)}\n\n"
        for key, value in self.connection_records.items():
            buffer+=f"{key}: {value}\n"
        buffer+="\n"
        return buffer

    def decode(self, data:str, cumul:str, ip=None):
        # parse the data
        #  try to parse data and if it fails, append it to the cumul string
        # print(data)
        cumul+=data
        if "{" in cumul and "}" in cumul:
            # isolate that data
            start = cumul.find("{")
            end = cumul.find("}")
            data = cumul[start+1:end]
            data_= data.split("/")
            cumul = ""
            if len(data_) == 3:
                group, key, val = data_
                val = float(val)
                print(f"Group: {group}, Key: {key}, Value: {val}")
                # return session, key, val, time, ip
                self.data.put((group, key, val, time.time(), ip[0]))
            else:
                print("Error: data is not in the right format")
        # else:
        #     print("data incomplete")
        return cumul
    
