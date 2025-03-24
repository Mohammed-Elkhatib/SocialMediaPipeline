# dashboard/python/scheduler.py
import subprocess
import threading
import time
import logging
from datetime import datetime
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("dashboard-scheduler")

# Get the project root directory (assuming this script is in dashboard/python/)
project_root = Path(__file__).parent.parent.parent


class DataRefreshScheduler:
    def __init__(self, interval_minutes=10, username="ALJADEEDNEWS"):
        self.interval_minutes = interval_minutes
        self.username = username
        self.running = False
        self.last_refresh_time = None
        self.scheduler_thread = None

    def run_main_script(self):
        """Run the main.py script with 'all' mode to fetch and process new data"""
        try:
            logger.info(f"Running data refresh at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Construct the path to main.py
            main_script_path = os.path.join(project_root, "main.py")

            # Use the specific Python executable from the virtual environment
            python_executable = sys.executable  # Get the current Python interpreter path

            # Run the main.py script with the 'all' mode
            process = subprocess.Popen(
                [python_executable, main_script_path, "--mode", "all", "--username", self.username],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Log stdout and stderr for debugging
            stdout, stderr = process.communicate()
            if stdout:
                logger.info(f"Main script output: {stdout.decode('utf-8')}")
            if stderr:
                logger.error(f"Main script error: {stderr.decode('utf-8')}")

            # Update the last refresh time
            self.last_refresh_time = datetime.now()

            logger.info(f"Data refresh completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error running main script: {str(e)}")
            return False

    def scheduler_loop(self):
        """Main scheduler loop that runs at the specified interval"""
        while self.running:
            try:
                # Run the main script to refresh data
                success = self.run_main_script()

                # Notify the SSE endpoints that data has been refreshed
                if success:
                    self.notify_data_refresh()

                # Sleep until the next interval
                logger.info(f"Sleeping for {self.interval_minutes} minutes until next refresh")
                for _ in range(self.interval_minutes * 60):  # Convert minutes to seconds
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(60)  # Sleep for a minute before retrying

    def notify_data_refresh(self):
        """
        Update the SSE system to notify clients about new data
        This method would need to interface with your SSE implementation
        """
        try:
            # For now, we'll just update a file that the SSE router can check
            sse_trigger_path = os.path.join(project_root, "dashboard", "python", "sse_trigger.txt")
            with open(sse_trigger_path, "w") as f:
                f.write(f"Data refreshed at {datetime.now().isoformat()}")
            logger.info("SSE refresh notification sent")
        except Exception as e:
            logger.error(f"Error notifying SSE: {str(e)}")

    def start(self):
        """Start the scheduler"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self.scheduler_loop)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            logger.info(f"Scheduler started with {self.interval_minutes} minute interval")

            # Run immediately on start
            initial_thread = threading.Thread(target=self.run_main_script)
            initial_thread.daemon = True
            initial_thread.start()

    def stop(self):
        """Stop the scheduler"""
        if self.running:
            self.running = False
            logger.info("Scheduler stopping")

    def get_status(self):
        """Get the current status of the scheduler"""
        return {
            "running": self.running,
            "interval_minutes": self.interval_minutes,
            "last_refresh": self.last_refresh_time.isoformat() if self.last_refresh_time else None
        }


# Create a singleton instance
scheduler = DataRefreshScheduler()


# Function to get the scheduler instance
def get_scheduler():
    return scheduler
