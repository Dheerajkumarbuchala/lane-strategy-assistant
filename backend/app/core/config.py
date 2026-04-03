"""
This file is to store the environment variables and configuration settings for the application
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

# get the google maps api key from environment variable
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
if not GOOGLE_MAPS_API_KEY:
    raise RuntimeError("GOOGLE_MAPS_API_KEY environment variable is not set.")