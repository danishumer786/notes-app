#!/bin/bash
# Launches the Flask app with Gunicorn when running on Azure App Service (Linux).
gunicorn --bind=0.0.0.0:${PORT:-8000} app:app
