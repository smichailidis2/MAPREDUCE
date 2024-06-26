import os
import sys
from kazoo.client import KazooClient
from kubernetes import client, config
import time

def initialize_zookeeper():
    zk_host = os.getenv('ZOOKEEPER_HOST')
    zk = KazooClient(hosts=zk_host)
    zk.start()
    return zk

def create_job(api_instance, job_manifest):
    try:
        api_response = api_instance.create_namespaced_job(
            body=job_manifest,
            namespace="sad")
        print("Job created. Status='%s'" % str(api_response.status))
    except client.exceptions.ApiException as e:
        print("Exception when creating job: %s\n" % e)

def create_worker_jobs(num_mappers, num_reducers):
    print("Creating Jobs")
    config.load_incluster_config()
    batch_v1 = client.BatchV1Api()

    # Create mappers
    for i in range(num_mappers):
        print(f"Mapper {i}")
        zk.ensure_path(f"/tomapp_{i}.txt")
        zk.set(f"/tomapp_{i}.txt",("word alpha beta alpha alpha word alpha beta").encode("utf-8"))
        
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
                                    {"name": "NODE_ID", "value": i}
                                ]
                            }
                        ],
                        "restartPolicy": "OnFailure"
                    }
                },
                "backoffLimit": 4
            }
        }
        result = create_job(batch_v1, job_manifest)
        # results.append({job_name: result})
    
    while True:
        all_done = True
        for i in range(num_mappers):
            if not zk.exists(f"mapper_done_{i}"):
                all_done = False
                break
        if all_done:
            for child in zk.get_children(f"/mapp_1"):
                data, _ = zk.get(f"/mapp_1/{child}")
                print(data.decode("utf-8"))
            break
            
    
    print(f"Mappers returned.")
    return
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
        result = create_job(batch_v1, job_manifest)
        # results.append({job_name: result})

if __name__ == "__main__":
    num_mappers = 3#int(os.getenv('NUM_MAPPERS', 3))
    num_reducers = 2#int(os.getenv('NUM_REDUCERS', 2))

    zk = initialize_zookeeper()
    # zk.ensure_path("/tasks")
    
    create_worker_jobs(num_mappers, num_reducers)
    
    print("Tasks assigned and jobs created.")
    zk.stop()
