"""
WSGI file for PythonAnywhere deployment
This file tells PythonAnywhere how to run the Flask application
"""

import os
import sys

# Get the project directory dynamically
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate virtualenv
activate_this = os.path.expanduser('~/.virtualenvs/flask/bin/activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})

# Import the Flask application
from app import app as application

# Initialize database on first deployment
db_path = os.path.join(project_home, 'esports_manager.db')
if not os.path.exists(db_path):
    from app import init_db, insert_sample_data
    init_db()
    insert_sample_data()
