from flask import Flask, request, jsonify
from kubernetes import client, config
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import uuid

app = Flask(__name__)

USER_DATA_DIR = '/path/to/user_data' #todo

def get_user_file_path(username): #todo
    return os.path.join(USER_DATA_DIR, f'{username}.json')

def create_user(username, password):
    if os.path.exists(get_user_file_path(username)):
        return False, "User already exists"
    
    user_data = {
        "username": username,
        "password_hash": password=generate_password_hash(password1, method='pbkdf2:sha256'),
        "token": str(uuid.uuid4())
    }
    
    with open(user_file_path, 'w') as user_file:
        json.dump(user_data, user_file)
    
    return True, "User created successfully"


def delete_user(username, password):
    if not os.path.exists(get_user_file_path(username)):
        return False, "User does not exist!"

    # todo


def get_user(username):
    user_file_path = get_user_file_path(username)
    if not os.path.exists(user_file_path):
        return None
    
    with open(user_file_path, 'r') as user_file:
        user_data = json.load(user_file)
    
    return user_data

def get_user_by_token(token):
    for filename in os.listdir(USER_DATA_DIR):
        file_path = os.path.join(USER_DATA_DIR, filename)
        with open(file_path, 'r') as user_file:
            user_data = json.load(user_file)
            if user_data['token'] == token:
                return user_data
    return None

def update_user(username, user_data):
    user_file_path = get_user_file_path(username)
    with open(user_file_path, 'w') as user_file:
        json.dump(user_data, user_file)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        token = token.replace('Bearer ', '')
        user_data = get_user_by_token(token)
        if not user_data:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(user_data, *args, **kwargs)
    return decorated_function

config.load_incluster_config()  # Use within a Kubernetes cluster
v1 = client.CoreV1Api()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    success, message = create_user(username, password)
    if not success:
        return jsonify({"message": message}), 400
    
    user_data = get_user(username)
    return jsonify({"message": "User registered successfully", "token": user_data['token']}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = user.get_token()
    return jsonify({"token": token}), 200
