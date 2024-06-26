import os
import sys
import time
from kazoo.client import KazooClient
import json

def initialize_zookeeper():
    zk_host = os.getenv('ZOOKEEPER_HOST')
    zk = KazooClient(hosts=zk_host)
    zk.start()
    return zk

def mapper():
    print("Running mapper task.")
    # Mapper logic here
    
    data, stat = zk.get(f"/tomapp_{node_id}.txt")
    
    results = {}
    words = data.decode("utf-8").split()
    for word in words:
        if word not in results:
            results[word] = 0
        results[word] += 1
    
    print("Mapped!!!\n")

    shuffler(results)

def shuffler(mapped_data):
    print("Running shuffler task.")
    # Shuffler logic here
    
    for key, value in mapped_data:
        print(f"{key}, {value}")
        zk.ensure_path(f"/mapp_{node_id}/{key}")
        zk.set(f"/mapp_{node_id}/{key}", (f"\"{key}\": {value}").encode("utf-8"))
    
    print("Shuffled!!!\n")

def reducer():
    print("Running reducer task.")
    # Reducer logic here
    
    data, stat = zk.get(f"/toreduce_{node_id}.txt")
    
    results = []
    words = data.decode("utf-8")
    for word in words:
        results.append((word, 1))
    
    print("Mapped!!!\n")

    shuffler(results)

    print("Reduced!!!\n")

if __name__ == "__main__":
    zk = initialize_zookeeper()
    node_id = os.getenv('NODE_ID')
    mode = os.getenv('MODE')

    # zk.get_children(zk_path, watch=None)

    if mode == 'mapper':
        mapper()
    elif mode == 'reducer':
        reducer()

    print(f"Node {node_id} completed {mode} task.")
    zk.stop()
