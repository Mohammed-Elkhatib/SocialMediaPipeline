import logging
import time
import os
import threading
import schedule
from datetime import datetime
from typing import Callable, Dict, Any, Optional

from src.analytics.service import AnalyticsService

logger = logging.getLogger(__name__)

class AnalyticsScheduler:
    """
    Scheduler for running analytics tasks at regular intervals.
    
    This class manages when analytics processes should run and ensures
    they don't overlap or conflict with each other.
    """
    
    def __init__(self, analytics_service: Optional[AnalyticsService] = None):
        """
        Initialize the scheduler with an optional analytics service.
        
        Args:
            analytics_service: An instance of AnalyticsService to use for running tasks
        """
        self.analytics_service = analytics_service or AnalyticsService()
        self.running_tasks = {}
        self.task_locks = {}
        self._terminate = False
        self._scheduler_thread = None
        
        logger.info("Analytics scheduler initialized")
    
    def _run_task_with_lock(self, task_name: str, task_func: Callable, **kwargs) -> None:
        """
        Run a task with a lock to prevent concurrent execution.
        
        Args:
            task_name: Name of the task for logging and locking
            task_func: The function to run
            **kwargs: Arguments to pass to the task function
        """
        # Create lock if it doesn't exist
        if task_name not in self.task_locks:
            self.task_locks[task_name] = threading.Lock()
            
        # Try to acquire the lock
        if not self.task_locks[task_name].acquire(blocking=False):
            logger.info(f"Task '{task_name}' is already running, skipping this run")
            return
            
        try:
            # Mark task as running
            self.running_tasks[task_name] = {
                'start_time': datetime.now(),
                'status': 'running'
            }
            
            # Run the task
            logger.info(f"Starting scheduled task: {task_name}")
            result = task_func(**kwargs)
            
            # Update task status
            self.running_tasks[task_name] = {
                'start_time': self.running_tasks[task_name]['start_time'],
                'end_time': datetime.now(),
                'status': 'completed',
                'success': True
            }
            
            logger.info(f"Completed scheduled task: {task_name}")
            return result
            
        except Exception as e:
            # Update task status on error
            self.running_tasks[task_name] = {
                'start_time': self.running_tasks[task_name]['start_time'],
                'end_time': datetime.now(),
                'status': 'failed',
                'success': False,
                'error': str(e)
            }
            
            logger.error(f"Error in scheduled task '{task_name}': {str(e)}", exc_info=True)
            
        finally:
            # Always release the lock
            self.task_locks[task_name].release()
    
    def schedule_word_frequency_analysis(self, 
                                        interval: str = 'day', 
                                        at: str = '00:00',
                                        time_period: Optional[int] = 7,
                                        platform: str = 'x',
                                        top_n: int = 100) -> None:
        """
        Schedule regular word frequency analysis.
        
        Args:
            interval: Interval type ('day', 'hour', 'week', 'month')
            at: Time to run (format depends on interval)
            time_period: Number of days to analyze
            platform: Platform to analyze
            top_n: Number of top words to include
        """
        task_name = f"word_frequency_analysis_{platform}"
        task_func = lambda: self._run_task_with_lock(
            task_name,
            self.analytics_service.run_word_frequency_analysis,
            time_period=time_period,
            platform=platform,
            top_n=top_n
        )
        
        # Schedule based on the interval
        if interval == 'day':
            schedule.every().day.at(at).do(task_func)
        elif interval == 'hour':
            schedule.every().hour.at(at).do(task_func)
        elif interval == 'week':
            schedule.every().week.at(at).do(task_func)
        elif interval == 'month':
            schedule.every().month.at(at).do(task_func)
        else:
            raise ValueError(f"Unsupported interval: {interval}")
            
        logger.info(f"Scheduled {task_name} to run every {interval} at {at}")
    
    def schedule_engagement_analysis(self,
                                   interval: str = 'day',
                                   at: str = '01:00',
                                   time_period: Optional[int] = 7,
                                   platform: str = 'x',
                                   top_n: int = 10) -> None:
        """
        Schedule regular engagement analysis.
        
        Args:
            interval: Interval type ('day', 'hour', 'week', 'month')
            at: Time to run (format depends on interval)
            time_period: Number of days to analyze
            platform: Platform to analyze
            top_n: Number of top tweets to include
        """
        task_name = f"engagement_analysis_{platform}"
        task_func = lambda: self._run_task_with_lock(
            task_name,
            self.analytics_service.run_engagement_analysis,
            time_period=time_period,
            platform=platform,
            top_n=top_n
        )
        
        # Schedule based on the interval
        if interval == 'day':
            schedule.every().day.at(at).do(task_func)
        elif interval == 'hour':
            schedule.every().hour.at(at).do(task_func)
        elif interval == 'week':
            schedule.every().week.at(at).do(task_func)
        elif interval == 'month':
            schedule.every().month.at(at).do(task_func)
        else:
            raise ValueError(f"Unsupported interval: {interval}")
            
        logger.info(f"Scheduled {task_name} to run every {interval} at {at}")
    
    def schedule_all_analyses(self,
                            interval: str = 'day',
                            at: str = '02:00',
                            time_period: Optional[int] = 7,
                            platform: str = 'x') -> None:
        """
        Schedule all analytics tasks.
        
        Args:
            interval: Interval type ('day', 'hour', 'week', 'month')
            at: Time to run (format depends on interval)
            time_period: Number of days to analyze
            platform: Platform to analyze
        """
        # Schedule individual analyses
        self.schedule_word_frequency_analysis(
            interval=interval,
            at=at,
            time_period=time_period,
            platform=platform
        )
        
        # Schedule engagement analysis 5 minutes later to avoid resource contention
        at_parts = at.split(':')
        hour = int(at_parts[0])
        minute = int(at_parts[1]) + 5
        if minute >= 60:
            minute -= 60
            hour = (hour + 1) % 24
        engagement_time = f"{hour:02d}:{minute:02d}"
        
        self.schedule_engagement_analysis(
            interval=interval,
            at=engagement_time,
            time_period=time_period,
            platform=platform
        )
        
        logger.info(f"All analyses scheduled to run every {interval}")
    
    def start(self) -> None:
        """Start the scheduler in a background thread."""
        if self._scheduler_thread is not None and self._scheduler_thread.is_alive():
            logger.warning("Scheduler is already running")
            return
            
        self._terminate = False
        self._scheduler_thread = threading.Thread(target=self._run_scheduler)
        self._scheduler_thread.daemon = True
        self._scheduler_thread.start()
        
        logger.info("Analytics scheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self._terminate = True
        if self._scheduler_thread is not None:
            self._scheduler_thread.join(timeout=5.0)
            
        logger.info("Analytics scheduler stopped")
    
    def _run_scheduler(self) -> None:
        """Run the scheduler loop."""
        logger.info("Scheduler thread started")
        while not self._terminate:
            schedule.run_pending()
            time.sleep(1)
        logger.info("Scheduler thread stopped")
    
    def get_task_status(self, task_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the status of scheduled tasks.
        
        Args:
            task_name: Name of specific task to check (None for all tasks)
            
        Returns:
            Dict containing task status information
        """
        if task_name:
            return self.running_tasks.get(task_name, {"status": "not_run"})
        return self.running_tasks
