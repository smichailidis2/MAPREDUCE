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
    
    data, stat = zk.get(f"/jobfiles_{jid}/tomapp_{node_id}")
    
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
        zk.ensure_path(f"/jobfiles_{jid}/mapp_{node_id}/{key}")
        zk.set(f"/jobfiles_{jid}/mapp_{node_id}/{key}", (str(mapped_data[key])).encode("utf-8"))
    
    print("Shuffled!!!\n")

def reducer():
    print("Running reducer task.")
    # Reducer logic here
    
    data_reduced  = {}
    for i in range(num_mappers):
        for child in zk.get_children(f"/jobfiles_{jid}/mapp_{i}"):
                if str(child) in words_to_reduce:
                    data, stat = zk.get(f"/jobfiles_{jid}/mapp_{i}/{child}")
                    if child not in data_reduced:
                        data_reduced[child] = 0
                    data_reduced[child] += int(data.decode("utf-8"))
                
    print(f"dr: {data_reduced}")

    zk.ensure_path(f"/jobfiles_{jid}/reduce_{node_id}")
    zk.set(f"/jobfiles_{jid}/reduce_{node_id}", (f"{data_reduced}").encode("utf-8"))
    print("Reduced!!!\n")

if __name__ == "__main__":
    zk = initialize_zookeeper()
    node_id = os.getenv('NODE_ID')
    mode = os.getenv('MODE')
    num_mappers = int(os.getenv('MAPPERS'))
    words_to_reduce = os.getenv('WORDS').split()
    jid = int(os.getenv('JOB_ID'))

    # zk.get_children(zk_path, watch=None)

    if mode == 'mapper':
        mapper()
        zk.ensure_path(f"/jobfiles_{jid}/mapper_done_{node_id}")
    elif mode == 'reducer':
        reducer()
        zk.ensure_path(f"/jobfiles_{jid}/reducer_done_{node_id}")

    print(f"Node {node_id} completed {mode} task.")
    zk.stop()
