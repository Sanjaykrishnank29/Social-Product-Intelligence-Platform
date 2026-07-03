import os
import sys
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from app.db.session import SessionLocal
from app.utils.pdf_generator import generate_weekly_pdf_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("report_generator")

def generate_weekly_report():
    db = SessionLocal()
    try:
        file_path, report = generate_weekly_pdf_report(db)
        logger.info(f"Weekly report generated successfully: {file_path}")
    except Exception as e:
        logger.error(f"Failed to generate weekly report: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_weekly_report()
