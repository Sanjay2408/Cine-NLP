from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# Add the parent directory to sys.path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app

# This is required for Vercel's Python runtime
app = app
