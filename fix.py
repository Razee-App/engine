import os

# List of directories to check
directories = [
    'app',
    'app/api',
    'app/api/v1',
    'app/api/v1/endpoints',
    'app/core',
    'app/models',
    'app/schemas',
    'app/services',
    'app/crud',
    'app/db',
    'app/tests',
    'app/utils'
]

# Function to check and create __init__.py
def ensure_init_py(directory_list):
    for directory in directory_list:
        init_file = os.path.join(directory, '__init__.py')
        if not os.path.exists(init_file):
            os.makedirs(directory, exist_ok=True)
            with open(init_file, 'w') as f:
                f.write("# This file makes this directory a package\n")
            print(f"Created __init__.py in {directory}")
        else:
            print(f"__init__.py already exists in {directory}")

if __name__ == "__main__":
    ensure_init_py(directories)
