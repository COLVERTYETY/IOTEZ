from fastapi import FastAPI, Request
import uvicorn
import os
import json
import pandas as pd
import numpy as np
import time
from socket_handler import *
from data_handler import *
from settings import *
import threading
from queue import Queue


app = FastAPI()

request_Q = Queue(maxsize=1000)

socket_actor = SocketActor()
data_actor = DataActor(socket_actor.data, request_Q)

@app.get("/sockets")
def get_connections():
    print(socket_actor)
    return socket_actor.status()

@app.get("/requests")
def get_ips():
    buffer = "{"
    for ip in data_actor.get_ips():
        buffer += ip + ","
    buffer = buffer[:-1]
    buffer += "}"
    return buffer

@app.put("/{group}/{key}/{value}")
def put(group:str, key:str, value:str, request:Request):
    #  get ip
    ip = request.client.host
    #  get time
    time_stamp = time.time()
    #  put in queue
    request_Q.put((group, key, value, time_stamp, ip))
    return {"ok"}

@app.get("/dump")
def dump():
    return data_actor.dump()

# @app.get("/{group}/{key}")
# def get(group:str, key:str):
#     print(group, key)
#     return data_actor.get(group, key).to_json()

@app.get("/{group}/{key}/{n}")
def get_last(group:str, key:str, n:int):
    return data_actor.get_last(group, key, n).to_json()

@app.get("/{group}/{key}/{time_start}/{time_stop}")
def get_window(group:str, key:str, time_start:int, time_stop:int):
    return data_actor.get_window(group, key, time_start, time_stop).to_json()

@app.get("/groups")
def get_groups():
    buffer="{"
    for group in data_actor.get_groups():
        buffer += group + ","
    buffer = buffer[:-1]
    buffer += "}"
    return buffer

@app.get("/keys/{group}")
def get_keys(group:str):
    buffer="{"
    for key in data_actor.get_keys(group):
        buffer += key + ","
    buffer = buffer[:-1]
    buffer += "}"
    return buffer



# @app.get("/all")
# def get_all():
#     return data_actor.get_all().copy()

@app.put("/save")
def save():
    path = data_actor.save()
    return f'{{path}}'


if __name__ == "__main__":
    print("STARTING SERVER")
    t1 = threading.Thread(target=data_actor.run)
    t2 = threading.Thread(target = socket_actor.run)
    t1.start()
    t2.start()
    uvicorn.run(app, host=IP, port=PORT_HTTP)
    print("SENDING STOP")
    socket_actor.stop()
    data_actor.stop()
    print("CLOSING THREADS")
    while t1.is_alive() or t2.is_alive():
        print(t1.is_alive(), t2.is_alive())
        time.sleep(1)
    print("DONE")