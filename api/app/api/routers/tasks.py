"""
Task Management Endpoints
========================

This module provides endpoints for monitoring and managing Celery tasks.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from celery.result import AsyncResult

from app.api.routers.auth import get_current_active_user
from app.celery_app import celery_app, TaskStatus

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}/status")
async def get_task_status(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get the status of a specific task"""
    try:
        # Get task result
        task_result = AsyncResult(task_id, app=celery_app)
        
        # Check if task exists
        if task_result.state == TaskStatus.PENDING:
            return {
                "task_id": task_id,
                "status": "pending",
                "progress": 0,
                "message": "Task is waiting to be processed"
            }
        
        # Get task info
        task_info = task_result.info or {}
        
        if task_result.state == TaskStatus.SUCCESS:
            return {
                "task_id": task_id,
                "status": "completed",
                "progress": 100,
                "message": "Task completed successfully",
                "result": task_result.result
            }
        elif task_result.state == TaskStatus.FAILURE:
            return {
                "task_id": task_id,
                "status": "failed",
                "progress": 0,
                "message": "Task failed",
                "error": str(task_info.get('exc_message', 'Unknown error'))
            }
        elif task_result.state == TaskStatus.STARTED:
            progress = task_info.get('progress', 0)
            message = task_info.get('message', 'Task in progress')
            return {
                "task_id": task_id,
                "status": "in_progress",
                "progress": progress,
                "message": message
            }
        elif task_result.state == TaskStatus.RETRY:
            return {
                "task_id": task_id,
                "status": "retrying",
                "progress": 0,
                "message": f"Task is being retried (attempt {task_info.get('retries', 0) + 1})"
            }
        else:
            return {
                "task_id": task_id,
                "status": task_result.state.lower(),
                "progress": 0,
                "message": f"Task status: {task_result.state}"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task status: {str(e)}")


@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Cancel a running task"""
    try:
        # Revoke the task
        celery_app.control.revoke(task_id, terminate=True)
        
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task has been cancelled"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling task: {str(e)}")


@router.get("/active")
async def get_active_tasks(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get all active tasks"""
    try:
        # Get active tasks from all workers
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        if not active_tasks:
            return {
                "active_tasks": [],
                "total_count": 0
            }
        
        # Flatten the results
        all_tasks = []
        for worker, tasks in active_tasks.items():
            for task in tasks:
                all_tasks.append({
                    "task_id": task.get('id'),
                    "name": task.get('name'),
                    "worker": worker,
                    "args": task.get('args', []),
                    "kwargs": task.get('kwargs', {}),
                    "time_start": task.get('time_start')
                })
        
        return {
            "active_tasks": all_tasks,
            "total_count": len(all_tasks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting active tasks: {str(e)}")


@router.get("/stats")
async def get_task_stats(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get task statistics"""
    try:
        # Get worker stats
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if not stats:
            return {
                "workers": [],
                "total_workers": 0,
                "total_active_tasks": 0
            }
        
        # Process stats
        worker_stats = []
        total_active = 0
        
        for worker, worker_stat in stats.items():
            active_tasks = worker_stat.get('total', {}).get('active_tasks', 0)
            total_active += active_tasks
            
            worker_stats.append({
                "worker": worker,
                "active_tasks": active_tasks,
                "total_tasks": worker_stat.get('total', {}).get('total_tasks', 0),
                "pool": worker_stat.get('pool', {}),
                "rusage": worker_stat.get('rusage', {})
            })
        
        return {
            "workers": worker_stats,
            "total_workers": len(worker_stats),
            "total_active_tasks": total_active
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task stats: {str(e)}")


@router.get("/queues")
async def get_queue_info(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get information about task queues"""
    try:
        # Get queue lengths from Redis
        from app.celery_app import REDIS_URL
        import redis
        
        redis_client = redis.from_url(REDIS_URL)
        
        # Get queue lengths
        queues = {
            "analysis": redis_client.llen("celery"),
            "default": redis_client.llen("celery"),
        }
        
        return {
            "queues": queues,
            "total_pending": sum(queues.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting queue info: {str(e)}")
