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
    config.load_incluster_config()
    batch_v1 = client.BatchV1Api()

    # Create mappers
    for i in range(num_mappers):
        job_name = f"worker-mapper-{i}"
        job_manifest = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {"name": job_name},
            "spec": {
                "template": {
                    "metadata": {"labels": {"app": "worker", "type": "mapper"}},
                    "spec": {
                        "containers": [
                            {
                                "name": "worker",
                                "image": "dkeramidas1/worker_node:v01",
                                "env": [
                                    {"name": "MODE", "value": "mapper"},
                                    {"name": "ZOOKEEPER_HOST", "value": "zookeeper-0.zookeeper,zookeeper-1.zookeeper,zookeeper-2.zookeeper:2181"},
                                    {"name": "NAMESPACE", "value": "sad"}
                                ]
                            }
                        ],
                        "restartPolicy": "Always"
                    }
                },
                "backoffLimit": 4
            }
        }
        create_job(batch_v1, job_manifest)

    # Create reducers
    for i in range(num_reducers):
        job_name = f"worker-reducer-{i}"
        job_manifest = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {"name": job_name},
            "spec": {
                "template": {
                    "metadata": {"labels": {"app": "worker", "type": "reducer"}},
                    "spec": {
                        "containers": [
                            {
                                "name": "worker",
                                "image": "dkeramidas1/worker_node:v01",
                                "env": [
                                    {"name": "MODE", "value": "reducer"},
                                    {"name": "ZOOKEEPER_HOST", "value": "zookeeper-0.zookeeper,zookeeper-1.zookeeper,zookeeper-2.zookeeper:2181"},
                                    {"name": "NAMESPACE", "value": "sad"},
                                    {"name": "NODE_ID", "value": str(i)}
                                ]
                            }
                        ],
                        "restartPolicy": "Always"
                    }
                },
                "backoffLimit": 4
            }
        }
        create_job(batch_v1, job_manifest)

# if __name__ == "__main__":
#     num_mappers = int(os.getenv('NUM_MAPPERS', 3))
#     num_reducers = int(os.getenv('NUM_REDUCERS', 2))

#     zk = initialize_zookeeper()
#     zk.ensure_path("/tasks")
    
#     create_worker_jobs(num_mappers, num_reducers)
    
#     print("Tasks assigned and jobs created.")
#     zk.stop()
