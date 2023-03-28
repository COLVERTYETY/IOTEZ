import pandas as pd
import numpy as np
import time
import json
import os
import threading
from queue import Queue
from settings import *

class DataActor():
    def __init__(self, socket_Q:Queue, request_Q:Queue)->None:
        self.socket_Q = socket_Q
        self.request_Q = request_Q
        self.data = pd.DataFrame()
        self.lock = threading.Lock()
        self.data["group"] = []
        self.data["ip"] = []
        self.data["key"] = []
        self.data["value"] = []
        self.data["time"] = []
        self.runnable = True
        self.current_path = None
        self.server_start = time.strftime("%Y%m%d-%H%M%S")
        if AUTO_LOAD:
            self.load_last()
        else:
            print("NO AUTO LOAD")


    def run(self)->None:
        last_save  = time.time()
        while self.runnable:
            if not self.socket_Q.empty():
                group, key,value, time_stamp, ip = self.socket_Q.get()
                with self.lock:
                    self.data = self.data.append({"group":group, "ip":ip, "key":key, "value":value, "time":time_stamp}, ignore_index=True)
                    # self.data.concat({"group":group, "ip":ip, "key":key, "value":value, "time":time_stamp}, ignore_index=True)
            if not self.request_Q.empty():
                group, key,value, time_stamp, ip = self.request_Q.get()
                with self.lock:
                    # self.data.concat({"group":group, "ip":ip, "key":key, "value":value, "time":time_stamp}, ignore_index=True)
                    self.data = self.data.append({"group":group, "ip":ip, "key":key, "value":value, "time":time_stamp}, ignore_index=True)
            if AUTO_SAVE and (time.time() - last_save) > AUTO_SAVE_INTERVAL:
                self.save()
                last_save = time.time()
                print("SAVED DATA")

    def get(self, group:str, key:str)->pd.DataFrame:
        with self.lock:
            return self.data[(self.data["group"]==group) & (self.data["key"]==key)]

    def get_groups(self)->list:
        with self.lock:
            return self.data["group"].unique()

    def get_keys(self, group:str)->list:
        with self.lock:
            return self.data[self.data["group"]==group]["key"].unique()
    
    def get_ips(self,)->list:
        with self.lock:
            return self.data["ip"].unique()

    def get_last(self, group:str, key:str, n=1)->pd.DataFrame:
        with self.lock:
            return self.data[(self.data["group"]==group) & (self.data["key"]==key)].tail(n)
    
    def get_window(self, group:str, key:str, time_start:int, time_stop:int)->pd.DataFrame:
        with self.lock:
            return self.data[(self.data["group"]==group) & (self.data["key"]==key) & (self.data["time"]>=time_start) & (self.data["time"]<=time_stop)]

    def get_all(self)->pd.DataFrame:
        with self.lock:
            return self.data
    
    def dump(self)->json:
        with self.lock:
            return self.data.to_json(orient="records")

    def load(self,path:str)->None:
        with self.lock:
            # load from json
            # self.data = pd.read_json(path, orient="records")
            # load from csv
            self.data = pd.read_csv(path)
            # print(self.data)
    
    def save(self)->None:
        # determine name from time
        if not self.current_path:
            name = self.server_start+"_to_" + time.strftime("%Y%m%d-%H%M%S")
            name = os.path.join(DATA_PATH, name+".csv")
            self.current_path = name
        else:
            name = self.current_path
        with self.lock:
            # save as csv
            self.data.to_csv(name, index=False)
            # save as json
            # self.data.to_json(name, orient="records")
        return name

    def clear(self)->None:
        with self.lock:
            self.data = pd.DataFrame()
            self.data["group"] = []
            self.data["ip"] = []
            self.data["key"] = []
            self.data["value"] = []
            self.data["time"] = []
    
    def load_last(self)->bool:
        files = os.listdir(DATA_PATH)
        files = [f for f in files if f.endswith(".csv")]
        files.sort()
        if len(files) > 0:
            try:
                # check if last file is older than autlo load age
                last_time = files[-1].split("_to_")[1]
                last_time = time.strptime(last_time, "%Y%m%d-%H%M%S.csv")
                last_time = time.mktime(last_time)
                if (time.time() - last_time) < AUTO_LOAD_AGE:
                    self.load(os.path.join(DATA_PATH, files[-1]))
                    print(self.data.head())
                    self.current_path = os.path.join(DATA_PATH, files[-1])
                    self.server_start = files[-1].split("_to_")[0] 
                    print("SERVER RECORDING START TIME", self.server_start)
                    print("LOADED LAST DATA", files[-1])
                    return True
                else:
                    print("LAST DATA FILE TOO OLD")
                    return False
            except Exception as e:
                print("ERROR LOADING LAST DATA", e)
                return False
        else:
            print("NO DATA FOUND")
            return False
    
    def __str__(self) -> str:
        buffer = ""
        for group in self.get_groups():
            buffer += f"Group: {group}\n"
            for key in self.get_keys(group):
                buffer += f"\tKey: {key}\n"
                buffer += f"\t\t{self.get_last(group, key, 1)}\n"
        return buffer
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def stop(self)->None:
        self.runnable = False
        self.save()
        print("STOPPED data handler")
        
    