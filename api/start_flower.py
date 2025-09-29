#!/usr/bin/env python3
"""
Flower Monitoring Startup Script
================================

This script starts Flower for monitoring Celery tasks and workers.
"""

import os
import sys
from celery import Celery

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import the Celery app
from app.celery_app import celery_app

if __name__ == '__main__':
    # Start Flower
    from flower.command import FlowerCommand
    from flower.app import Flower
    
    flower = Flower(celery_app=celery_app)
    flower.run(
        address='0.0.0.0',
        port=5555,
        broker_api=celery_app.broker_connection().as_uri(),
        basic_auth='admin:admin'  # Change this in production
    )
