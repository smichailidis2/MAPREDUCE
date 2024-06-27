import click
import requests

# URLs for services
REGISTRATION_URL = "http://flask-app-pod.sad.svc.cluster.local:5001/register"
LOGIN_URL = "http://flask-app-pod.sad.svc.cluster.local:5001/login"
JOB_SUBMISSION_URL = "http://master-service.sad.svc.cluster.local:5000/submit_job"

@click.group()
def cli():
    """MapReduce Job Submission and User Management CLI."""
    pass

@click.command()
@click.option('--username', required=True, help="User's username")
@click.option('--password', required=True, help="User's password")
def register(username, password):
    """Register a new user."""
    payload = {'username': username, 'password': password}
    response = requests.post(REGISTRATION_URL, json=payload)
    if response.status_code == 200:
        click.echo("Registration successful.")
    else:
        click.echo(f"Failed to register: {response.text}")

@click.command()
@click.option('--username', required=True, help="User's username")
@click.option('--password', required=True, help="User's password")
def login(username, password):
    """Login a user."""
    payload = {'username': username, 'password': password}
    response = requests.post(LOGIN_URL, json=payload)
    if response.status_code == 200:
        click.echo("Login successful.")
    else:
        click.echo(f"Failed to login: {response.text}")

@click.command()
@click.option('--num-mappers', default=3, type=int, help="Number of mapper jobs (default: 3)")
@click.option('--num-reducers', default=2, type=int, help="Number of reducer jobs (default: 2)")
def submit_job(num_mappers, num_reducers):
    """Submit a new MapReduce job to the master service."""
    payload = {
        'mapper_num': num_mappers,
        'reducer_num': num_reducers
    }
    response = requests.post(JOB_SUBMISSION_URL, json=payload)
    if response.status_code == 200:
        click.echo("Job submitted successfully.")
        click.echo(response.json())
    else:
        click.echo(f"Failed to submit job: {response.status_code} - {response.text}")


# Adding commands to the CLI group
cli.add_command(register)
cli.add_command(login)
cli.add_command(submit_job)

if __name__ == '__main__':
    cli()
