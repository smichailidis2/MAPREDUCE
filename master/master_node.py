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
        zk.ensure_path(f"/jobfiles_{jid}/tomapp_{i}")
        zk.set(f"/jobfiles_{jid}/tomapp_{i}",dataToMapp[i].encode("utf-8"))
        # zk.set (f"/jobfiles_{jid}/tomapp_{i}",("word alpha beta alpha\nalpha word alpha beta").encode("utf-8"))
        
        job_name = f"worker-mapper-{jid}{i}"
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
                                    {"name": "NODE_ID", "value": str(i)},
                                    {"name": "WORDS", "value": "none"},
                                    {"name": "MAPPERS", "value": "0"},
                                    {"name": "JOB_ID", "value": str(jid)}
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
    
    while True:
        all_done = True
        for i in range(num_mappers):
            if not zk.exists(f"/jobfiles_{jid}/mapper_done_{i}"):
                all_done = False
                break
        if all_done:
            break

    print(f"Mappers returned.")
    
    all_words_to_reduce = []
    for i in range(num_mappers):
        for child in zk.get_children(f"/jobfiles_{jid}/mapp_{i}"):
                if str(child) not in all_words_to_reduce:
                    all_words_to_reduce.append(str(child))
        
    data_to_reduce  = [""]*num_reducers 

    for i, word in enumerate(all_words_to_reduce):
        data_to_reduce[(i+1) % num_reducers] += word
        data_to_reduce[(i+1) % num_reducers] += " "

    # Create reducers
    for i in range(num_reducers):
        job_name = f"worker-reducer-{jid}{i}"
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
                                    {"name": "WORDS", "value": data_to_reduce[i]},
                                    {"name": "MAPPERS", "value": str(num_mappers)},
                                    {"name": "JOB_ID", "value": str(jid)}
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
        
    while True:
        all_done = True
        for i in range(num_reducers):
            if not zk.exists(f"/jobfiles_{jid}/reducer_done_{i}"):
                all_done = False
                break
        if all_done:
            break

    print(f"Reducers returned.")
    
    mapreduceres = {}
    for i in range(num_reducers):
        data,_ = zk.get(f"/jobfiles_{jid}/reduce_{i}")
        mapreduceres.update(eval(data.decode("utf-8")))
    
    print(mapreduceres)

    zk.ensure_path(f"/jobres_{jid}")
    
    zk.set(f"/jobres_{jid}",(f"mapreduceres").encode("utf-8"))


if __name__ == "__main__":
    num_mappers = int(os.getenv('NUM_MAPPERS', 3))
    num_reducers = int(os.getenv('NUM_REDUCERS', 2))
    
    jid = int(os.getenv('JOB_ID',0))

    zk = initialize_zookeeper()
    # zk.ensure_path("/tasks")

    zk.ensure_path(f"/job_{jid}_inprocess")

    zk.ensure_path(f"/jobfiles_{jid}")

    zk.ensure_path(f"/user_in_job_{jid}")
    zk.set(f"/user_in_job_{jid}", ("3 2 1").encode("utf-8"))
    
    zk.ensure_path(f"/user_in_data_{jid}")
    zk.set(f"/user_in_data_{jid}",("word alpha beta alpha alpha word alpha beta\nword alpha beta alpha\nalpha word alpha beta gamma\nword alpha beta alpha\nalpha word alpha beta delta").encode("utf-8"))

    userIn, _ = zk.get(f"/user_in_job_{jid}")
    userData, _ = zk.get(f"/user_in_data_{jid}")

    userIn = userIn.decode("utf-8").split()
    num_mappers = int(userIn[0])
    num_reducers = int(userIn[1]) 
    jid = int(userIn[2]) 
        
    userData = userData.decode("utf-8").split('\n')
    dataToMapp = [""]*num_mappers
    for i, line in enumerate(userData):
        dataToMapp[i % num_mappers] += line
        dataToMapp[i % num_mappers] += " "

    create_worker_jobs(num_mappers, num_reducers)
    
    print("Tasks assigned and jobs created.")
    zk.delete(f"/job_{jid}_inprocess",-1,True)
    
    zk.delete(f"/jobfiles_{jid}",-1,True)

    zk.stop()
