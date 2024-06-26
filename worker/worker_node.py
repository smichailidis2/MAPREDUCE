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
    
    data, stat = zk.get(f"/tomapp_{node_id}")
    
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

    for key in mapped_data:
        print(f"{key}, {mapped_data[key]}")
        zk.ensure_path(f"/mapp_{node_id}/{key}")
        zk.set(f"/mapp_{node_id}/{key}", (str(mapped_data[key])).encode("utf-8"))
    
    print("Shuffled!!!\n")

def reducer():
    print("Running reducer task.")
    # Reducer logic here
    
    data, stat = zk.get(f"/toreduce_{node_id}")
    d = dict(data.decode("utf-8"))
    results = {}
    for word in d:
        print(f"{word}::: {d}: {d[word]}")
        if word not in results:
            results[word] = 0
        results[word] += sum(d[word])

    zk.ensure_path(f"/reduce_{node_id}")
    zk.set(f"/reduce_{node_id}", (f"{results}").encode("utf-8"))
    print("Reduced!!!\n")

if __name__ == "__main__":
    zk = initialize_zookeeper()
    node_id = os.getenv('NODE_ID')
    mode = os.getenv('MODE')

    # zk.get_children(zk_path, watch=None)

    if mode == 'mapper':
        mapper()
        zk.ensure_path(f"mapper_done_{node_id}")
    elif mode == 'reducer':
        reducer()
        zk.ensure_path(f"reducer_done_{node_id}")

    print(f"Node {node_id} completed {mode} task.")
    zk.stop()
