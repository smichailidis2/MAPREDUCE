import requests
import json

BASE_URL_MASTER = 'http://master-service.sad.svc.cluster.local:5000'
BASE_URL_AUTH = 'http://flask-app-service.sad.svc.cluster.local:5001'

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

def create_jobs(map, red):
    url = f"{BASE_URL_MASTER}/submit_job"
    payload = {'mapper_num': map, 'reducer_num': red}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {123}'
    }
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response

if __name__ == '__main__':
    username = 'testuser'
    password = 'testpass'
    
    # # Register user
    # register_response = register_user(username, password)
    # print('Register Response:', register_response.json())
    
    # # Login user
    # login_response = login_user(username, password)
    # print('Login Response:', login_response.json())
    
    # token = login_response.json().get('token')
    
    # Create jobs
    job_response = create_jobs(3, 2)
    print('Create Jobs Response:', job_response.json())
