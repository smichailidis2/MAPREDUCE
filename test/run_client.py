import requests
import json

BASE_URL_MASTER = 'http://master-service.sad.svc.cluster.local:5000'
BASE_URL_AUTH = 'http://flask-pod-service.sad.svc.cluster.local:5001'

def register_user(username, password):
    url = f"{BASE_URL_AUTH}/register"
    payload = {'username': username, 'password': password}
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response

def login_user(username, password):
    url = f"{BASE_URL_AUTH}/login"
    payload = {'username': username, 'password': password}
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response

def create_jobs(token, job_type, num_jobs):
    url = f"{BASE_URL_MASTER}/create_jobs"
    payload = {'mapper_num': job_type, 'reducer_num': num_jobs}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response

if __name__ == '__main__':
    username = 'testuser'
    password = 'testpass'
    
    # Register user
    register_response = register_user(username, password)
    print('Register Response:', register_response.json())
    
    # Login user
    login_response = login_user(username, password)
    print('Login Response:', login_response.json())
    
    token = login_response.json().get('token')
    
    # Create jobs
    job_response = create_jobs(token, 'mapper', 3)
    print('Create Jobs Response:', job_response.json())
