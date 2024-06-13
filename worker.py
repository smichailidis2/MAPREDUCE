import os, json
from importlib import util

def load_function(module_name, function_name):
    spec = util.spec_from_file_location(module_name, f"{module_name}.py")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)

def map_phase(filename, map_func):
    with open(filename, 'r') as f:
        data = f.readlines()
    
    map_results = []
    for line in data:
        map_results.extend(map_func(line.strip()))
    
    with open('map_output.json', 'w') as f:
        json.dump(map_results, f)
        
def shuffle_phase():
    with open('map_output.json', 'r') as f:
        map_result = json.load(f)

def reduce_phase(reduce_func):
    # Read input
    with open('shuffle_output.json', 'r') as f:
        shuffle_result = json.load(f)
    
    current_key = None
    current_values = []
    final_result = []

    for key, value in shuffle_result:
        if key != current_key:
            if key != None:
                final_result.append(current_key, current_values)
            current_key = key
            current_values = [value]
        else:
            current_values.append(value)
        
    if current_key is not None:
        final_result.append(reduce_func(current_key, current_values))

    with open('reduse_output.json', 'w') as f:
        json.dump(final_result, f)

def main():
    token = os.getenv('TOKEN')
    filename = os.getenv('FILENAME')
    role = os.getenv('ROLE')
    map_function_name = os.getenv('MAP_FUNCTION')
    reduce_function_name = os.getenv('REDUCE_FUNCTION')

    # Map/reduse/shuffle opperation
    if role == 'mapper':
        map_function = load_function('map_function', map_function_name)
    elif role == 'shuffler':
        pass
    elif role == 'reducer':
        reduce_function = load_function('reduce_function', reduce_function_name)

    # write to shared file system

if __name__ == '__main__':
    main()