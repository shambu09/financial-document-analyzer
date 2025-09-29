#!/usr/bin/env python3
"""
Celery Worker Startup Script
============================

This script starts a Celery worker for processing financial document analysis tasks.
"""

import os
import sys
from celery import Celery

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import the Celery app
from app.celery_app import celery_app

if __name__ == '__main__':
    # Start the worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=2',
        '--queues=analysis,celery',
        '--hostname=worker@%h'
    ])
