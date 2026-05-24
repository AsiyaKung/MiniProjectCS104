"""
WSGI file for PythonAnywhere deployment
This file tells PythonAnywhere how to run the Flask application
"""

import os
import sys

# Add the project directory to the Python path
project_home = '/home/yourusername/esports-team-manager'  # Replace 'yourusername' with your PythonAnywhere username
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask application
from app import app as application

# Initialize database on first deployment
if not os.path.exists(os.path.join(project_home, 'esports_manager.db')):
    from app import init_db, insert_sample_data
    init_db()
    insert_sample_data()
