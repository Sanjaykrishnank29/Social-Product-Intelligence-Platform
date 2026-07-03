import os
import sys
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from orchestrator import run_all
from reports.report_generator import generate_weekly_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("scheduler")

def main():
    scheduler = BlockingScheduler()
    
    # Schedule the unified pipeline every 6 hours
    scheduler.add_job(
        run_all,
        trigger=IntervalTrigger(hours=6),
        id="unified_pipeline_6h",
        name="Run Unified Pipeline Every 6 Hours",
        replace_existing=True
    )
    
    # Schedule weekly report generation
    scheduler.add_job(
        generate_weekly_report,
        trigger=IntervalTrigger(days=7),
        id="weekly_report",
        name="Generate Weekly Intelligence Report",
        replace_existing=True
    )
    
    logger.info("=== APScheduler Started ===")
    logger.info("Jobs Configured:")
    for job in scheduler.get_jobs():
        logger.info(f" - {job.name} (ID: {job.id}) | Next run at: {job.next_run_time}")
        
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutting down...")

if __name__ == "__main__":
    main()
