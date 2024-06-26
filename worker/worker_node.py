import os
import sys
import time
from kazoo.client import KazooClient
from mapreducef import mapperf
from mapreducef import reducerf

def initialize_zookeeper():
    zk_host = os.getenv('ZOOKEEPER_HOST')
    zk = KazooClient(hosts=zk_host)
    zk.start()
    return zk

def mapper():
    # print("Running mapper task.")
    # Mapper logic here
    print("Mapped!!!\n")
    
    # if(zk.exists(f"/mapreduce/inmapper_{node_id}.txt")):
    #     data, stat = zk.get(f"/mapreduce/inmapper_{node_id}.txt")
    
    # results = []
    # words = data.decode("utf-8").split()
    # for word in words:
    #     results.append((word, 1))
    
    # if(zk.exists(f"/mapreduce/shuffled_{node_id}.txt")):
    #     zk.set(f"/mapreduce/shuffled_{node_id}.txt", shuffler(results).encode("utf-8"))
    # else:
    #     zk.create(f"/mapreduce/shuffled_{node_id}.txt", shuffler(results).encode("utf-8"))

def shuffler(mapped_data):
    # print("Running shuffler task.")
    # Shuffler logic here
    
    shuffled_data = {}
    for key, value in mapped_data:
        if key not in shuffled_data:
            shuffled_data[key] = []
        shuffled_data[key].append(value)
    return shuffled_data

def reducer():
    # print("Running reducer task.")
    # Reducer logic here
    print("Reduced!!!\n")
    # if(zk.ensure_path(f"/mapreduce/inshuffler_{node_id}.txt")):
    #     shuffled_data, stat = zk.get(f"/mapreduce/inshuffler_{node_id}.txt")
    
    # reduced_data = []
    # for key, values in shuffled_data.decode("utf-8").items():
    #     reduced_data.append((key, sum(values)))
    
    # if(zk.exists(f"/mapreduce/reduced_{node_id}.txt")):
    #     zk.set(f"/mapreduce/reduced_{node_id}.txt", shuffler(reduced_data).encode("utf-8"))
    # else:
    #     zk.create(f"/mapreduce/reduced_{node_id}.txt", shuffler(reduced_data).encode("utf-8"))

if __name__ == "__main__":
    zk = initialize_zookeeper()
    zk_path = "/mapreduce"
    node_id = os.getenv('NODE_ID')
    mode = os.getenv('MODE')

    # zk.get_children(zk_path, watch=None)

    if mode == 'mapper':
        mapper()
    elif mode == 'reducer':
        reducer()

    # print(f"Node {node_id} completed {mode} task.")
    zk.stop()
