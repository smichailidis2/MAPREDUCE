import click
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kazoo.client import KazooClient
import yaml

config.load_incluster_config()
batch_v1 = client.BatchV1Api()

@click.group()
def cli():
    """MapReduce Job Submission CLI."""
    pass

@click.command()
@click.option('--input-data', type=click.File('rb'), help='File containing input data for the mapper')
@click.option('--node-id', required=True, help='Unique node ID for the mapper')
def submit_mapper(input_data, node_id):
    """Submit a new Mapper job."""
    job_manifest = load_yaml_file('mapper-job.yaml')
    zk = connect_to_zookeeper()  
    try:
        input_path = f"/tomapp_{node_id}.txt"
        zk.ensure_path(input_path)
        zk.set(input_path, input_data.read())
        zk.stop() 
        api_response = batch_v1.create_namespaced_job(body=job_manifest, namespace="sad")
        click.echo(f"Mapper job submitted. Status='{api_response.status}'")
    except ApiException as e:
        zk.stop()
        click.echo(f"Exception when creating mapper job: {e}")

@click.command()
@click.option('--input-data', type=click.File('rb'), help='File containing input data for the reducer')
@click.option('--node-id', required=True, help='Unique node ID for the reducer')
def submit_reducer(input_data, node_id):
    """Submit a new Reducer job."""
    job_manifest = load_yaml_file('reducer-job.yaml')
    zk = connect_to_zookeeper()
    try:
        input_path = f"/toreduce_{node_id}.txt"
        zk.ensure_path(input_path)
        zk.set(input_path, input_data.read())
        zk.stop()
        api_response = batch_v1.create_namespaced_job(body=job_manifest, namespace="sad")
        click.echo(f"Reducer job submitted. Status='{api_response.status}'")
    except ApiException as e:
        zk.stop()
        click.echo(f"Exception when creating reducer job: {e}")

@click.command()
@click.argument('job_name')
def status(job_name):
    """Check the status of a job."""
    try:
        job_status = batch_v1.read_namespaced_job_status(job_name, "sad")
        click.echo(f"Job {job_name} status: {job_status.status}")
    except ApiException as e:
        click.echo(f"Error retrieving job status: {e}")

def load_yaml_file(file_path):
    """Utility function to load a YAML file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def connect_to_zookeeper():
    """Utility function to connect to ZooKeeper."""
    zk_host = "zk-cs.sad.svc.cluster.local:2181"
    zk = KazooClient(hosts=zk_host)
    zk.start()
    return zk

cli.add_command(submit_mapper)
cli.add_command(submit_reducer)
cli.add_command(status)

if __name__ == '__main__':
    cli()
