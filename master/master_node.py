import os
import sys
from kazoo.client import KazooClient
from kubernetes import client, config
import time
import json

def initialize_zookeeper():
    zk_host = os.getenv('ZOOKEEPER_HOST')
    zk = KazooClient(hosts=zk_host)
    zk.start()
    return zk

def create_job(api_instance, job_manifest, mode, id):
    try:
        api_response = api_instance.create_namespaced_job(
            body=job_manifest,
            namespace="sad")
        print(f"Job created. Status='{mode}: {id}'")# % str(api_response.status))
    except client.exceptions.ApiException as e:
        print("Exception when creating job: %s\n" % e)

def create_worker_jobs(num_mappers, num_reducers):
    print("Creating Jobs")
    config.load_incluster_config()
    batch_v1 = client.BatchV1Api()

    # Create mappers
    for i in range(num_mappers):
        print(f"Mapper {i}")
        zk.ensure_path(f"/tomapp_{i}")
        zk.set (f"/tomapp_{i}",("word alpha beta alpha alpha word alpha beta").encode("utf-8"))
        
        job_name = f"worker-mapper-{i}"
        job_manifest = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {"name": job_name, "namespace": "sad"},
            "spec": {
                "template": {
                    "metadata": {"labels": {"app": "worker", "type": "mapper"}},
                    "spec": {
                        "containers": [
                            {
                                "name": "worker",
                                "image": "dkeramidas1/worker_node:v01",
                                "imagePullPolicy": "Always",
                                "env": [
                                    {"name": "MODE", "value": "mapper"},
                                    {"name": "ZOOKEEPER_HOST", "value": "zk-cs.sad.svc.cluster.local:2181"},
                                    {"name": "NAMESPACE", "value": "sad"},
                                    {"name": "NODE_ID", "value": str(i)}
                                ]
                            }
                        ],
                        "restartPolicy": "OnFailure"
                    }
                },
                "backoffLimit": 4
            }
        }
        result = create_job(batch_v1, job_manifest, "Mapper", i)
        # results.append({job_name: result})
    
    print(f"Mappers instanciated.")
    while True:
        all_done = True
        for i in range(num_mappers):
            if not zk.exists(f"mapper_done_{i}"):
                all_done = False
                break
        if all_done:
            break

    print(f"Mappers returned.")
    
    data_to_reduce  = {}
    for i in range(num_mappers):
        for child in zk.get_children(f"/mapp_{i}"):
                data, stat = zk.get(f"/mapp_{i}/{child}")
                d = data.decode("utf-8")
                if child not in data_to_reduce:
                    data_to_reduce[child] = []
                data_to_reduce[child].append(int(d))
                
    print(f"dr: {data_to_reduce}")
    toreduce = []
    for i in range(num_reducers):
        toreduce.append({})

    print(toreduce)

    for i, word in enumerate(data_to_reduce):
        if word not in toreduce[num_mappers % (i+1)]:
            toreduce[num_mappers % (i+1)][word] = []
        toreduce[num_mappers % (i+1)][word].extend(data_to_reduce[word])
    
    print(toreduce)

    for i in range(num_reducers):
        print(f"{i}: {toreduce[i]}")
        zk.ensure_path(f"/toreduce_{i}")
        zk.set(f"/toreduce_{i}", (f"{toreduce[i]}").encode("utf-8"))

    # Create reducers
    for i in range(num_reducers):
        job_name = f"worker-reducer-{i}"
        job_manifest = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {"name": job_name, "namespace": "sad"},
            "spec": {
                "template": {
                    "metadata": {"labels": {"app": "worker", "type": "reducer"}},
                    "spec": {
                        "containers": [
                            {
                                "name": "worker",
                                "image": "dkeramidas1/worker_node:v01",
                                "imagePullPolicy": "Always",
                                "env": [
                                    {"name": "MODE", "value": "reducer"},
                                    {"name": "ZOOKEEPER_HOST", "value": "zk-cs.sad.svc.cluster.local:2181"},
                                    {"name": "NAMESPACE", "value": "sad"},
                                    {"name": "NODE_ID", "value": str(i)},
                                    {"name": "WORDS", "value": ""}
                                ]
                            }
                        ],
                        "restartPolicy": "OnFailure"
                    }
                },
                "backoffLimit": 4
            }
        }
        result = create_job(batch_v1, job_manifest, "reduce", i)
        # results.append({job_name: result})
        
    print(f"Reducers instanciated.")
    while True:
        all_done = True
        for i in range(num_reducers):
            if not zk.exists(f"reducer_done_{i}"):
                all_done = False
                break
        if all_done:
            break

    print(f"Reducers returned.")
    
    mapreduceres = {}
    for i in range(num_reducers):
        data,_ = zk.get(f"/reduce_{i}")
        mapreduceres.update(data.decode("utf-8"))
    
    print(mapreduceres)


if __name__ == "__main__":
    num_mappers = 3#int(os.getenv('NUM_MAPPERS', 3))
    num_reducers = 2#int(os.getenv('NUM_REDUCERS', 2))

    zk = initialize_zookeeper()
    # zk.ensure_path("/tasks")
    
    create_worker_jobs(num_mappers, num_reducers)
    
    print("Tasks assigned and jobs created.")
    zk.stop()
