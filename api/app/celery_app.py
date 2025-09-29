"""
Celery Configuration and Task Definitions
========================================

This module sets up Celery for background task processing in the financial document analyzer.
"""

import os
from celery import Celery
from celery.signals import worker_ready, worker_shutdown
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    'financial_analyzer',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['app.celery_tasks']
)

# Celery configuration
celery_app.conf.update(
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task execution
    task_always_eager=False,  # Set to True for testing
    task_eager_propagates=True,
    
    # Task routing
    task_routes={
        'app.celery_tasks.process_comprehensive_analysis': {'queue': 'analysis'},
        'app.celery_tasks.process_investment_analysis': {'queue': 'analysis'},
        'app.celery_tasks.process_risk_analysis': {'queue': 'analysis'},
        'app.celery_tasks.process_verification_analysis': {'queue': 'analysis'},
    },
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Task retry settings
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Worker signals
@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Called when worker is ready to accept tasks"""
    print(f"Celery worker {sender} is ready to accept tasks")

@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwargs):
    """Called when worker is shutting down"""
    print(f"Celery worker {sender} is shutting down")

# Task status constants
class TaskStatus:
    PENDING = 'PENDING'
    STARTED = 'STARTED'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    RETRY = 'RETRY'
    REVOKED = 'REVOKED'
