import click
from kazoo.client import KazooClient

def connect_to_zookeeper():
    """Connect to the ZooKeeper."""
    zk_host = "zk-cs.sad.svc.cluster.local:2181"  # Adjust if necessary
    zk = KazooClient(hosts=zk_host)
    zk.start()
    return zk

@click.group()
def cli():
    """MapReduce Job Submission CLI."""
    pass

@click.command()
@click.option('--job-id', required=True, type=int, help='Unique Job ID')
@click.option('--num-mappers', required=True, type=int, help='Number of mappers')
@click.option('--num-reducers', required=True, type=int, help='Number of reducers')
@click.option('--input-data', type=click.File('rb'), help='File containing input data')
def submit_job(job_id, num_mappers, num_reducers, input_data):
    """Submit a new job to the system."""
    zk = connect_to_zookeeper()
    try:
        job_input_path = f"/userin_job{job_id}"
        job_data = f"{num_mappers} {num_reducers} {job_id}"
        zk.ensure_path(job_input_path)
        zk.set(job_input_path, job_data.encode('utf-8'))
        click.echo("Input data successfully loaded to ZooKeeper.")
    finally:
        zk.stop()

cli.add_command(submit_job)

if __name__ == '__main__':
    cli()
