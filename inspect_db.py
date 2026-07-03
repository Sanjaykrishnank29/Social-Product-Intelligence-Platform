import os
import sys

# If POSTGRES_HOST is set to "db" or is empty, override it to "localhost" for host execution
if os.environ.get("POSTGRES_HOST") == "db" or not os.environ.get("POSTGRES_HOST"):
    os.environ["POSTGRES_HOST"] = "localhost"

# Add backend directory to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

try:
    from app.db.session import SessionLocal
    from app.db.models.mention import RawMention, ProcessedMention, AspectResult, TopicResult
except ImportError as e:
    print(f"Error importing database session or models: {e}")
    sys.exit(1)

def print_table(title, headers, rows):
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80)
    if not rows:
        print(" (No records found) ")
    else:
        try:
            from tabulate import tabulate
            print(tabulate(rows, headers=headers, tablefmt="grid"))
        except ImportError:
            # Fallback to custom simple formatting if tabulate is not available
            col_widths = [len(h) for h in headers]
            for row in rows:
                for idx, val in enumerate(row):
                    col_widths[idx] = max(col_widths[idx], len(str(val)))
            
            # Print headers
            header_str = " | ".join(f"{str(h).ljust(col_widths[i])}" for i, h in enumerate(headers))
            print(header_str)
            print("-" * len(header_str))
            
            # Print rows
            for row in rows:
                print(" | ".join(f"{str(val).ljust(col_widths[i])}" for i, val in enumerate(row)))
    print("="*80 + "\n")

def main():
    print(f"Connecting to database at {os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT', '5432')}...")
    
    try:
        db = SessionLocal()
        # Force a connection test query
        db.execute(RawMention.__table__.select().limit(1))
    except Exception as e:
        print("\n[ERROR] Could not connect to the PostgreSQL database.")
        print(f"Details: {e}")
        print("\nTips:")
        print("1. Make sure your Docker container is running: 'docker-compose up -d db'")
        print("2. Make sure your environment variables in '.env' match your running DB.")
        print("3. Check if 'POSTGRES_HOST' is set to 'localhost' if running this script directly on your host machine.")
        sys.exit(1)

    try:
        # 1. Row counts
        raw_count = db.query(RawMention).count()
        processed_count = db.query(ProcessedMention).count()
        aspect_count = db.query(AspectResult).count()
        topic_count = db.query(TopicResult).count()

        print("\nDatabase Summary:")
        print(f" - raw_mentions count        : {raw_count}")
        print(f" - processed_mentions count  : {processed_count}")
        print(f" - aspect_results count      : {aspect_count}")
        print(f" - topic_results count       : {topic_count}")

        # Ask what to show
        print("\nSelect an option to view sample records:")
        print("1. Show Raw Mentions (raw_mentions)")
        print("2. Show Cleaned & Processed Mentions (processed_mentions)")
        print("3. Show Aspect Results (aspect_results)")
        print("4. Show Topic Modeling Results (topic_results)")
        print("5. Exit")
        
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            limit = 5
            rows = db.query(RawMention).order_by(RawMention.id.desc()).limit(limit).all()
            headers = ["ID", "Brand", "Source", "External ID", "Rating", "Author", "Content Snippet"]
            data = [
                [r.id, r.brand, r.source, r.external_id, r.rating, r.author, (r.content[:50] + "...") if len(r.content) > 50 else r.content]
                for r in rows
            ]
            print_table(f"Last {limit} Ingested Raw Mentions (raw_mentions)", headers, data)
            
        elif choice == '2':
            limit = 5
            rows = db.query(ProcessedMention).order_by(ProcessedMention.id.desc()).limit(limit).all()
            headers = ["ID", "Source ID", "Brand", "Source", "Sentiment", "Score", "Cleaned Text Snippet"]
            data = [
                [r.id, r.source_id, r.brand, r.source, r.sentiment_label, f"{r.sentiment_score:.4f}" if r.sentiment_score else "N/A", (r.cleaned_text[:50] + "...") if len(r.cleaned_text) > 50 else r.cleaned_text]
                for r in rows
            ]
            print_table(f"Last {limit} Processed Mentions (processed_mentions)", headers, data)
            
        elif choice == '3':
            limit = 10
            rows = db.query(AspectResult).order_by(AspectResult.id.desc()).limit(limit).all()
            headers = ["ID", "Source ID", "Brand", "Aspect", "Sentiment", "Score"]
            data = [
                [r.id, r.source_id, r.brand, r.aspect, r.sentiment_label, f"{r.sentiment_score:.4f}"]
                for r in rows
            ]
            print_table(f"Last {limit} Aspect Extractions (aspect_results)", headers, data)
            
        elif choice == '4':
            limit = 10
            rows = db.query(TopicResult).order_by(TopicResult.id.desc()).limit(limit).all()
            headers = ["ID", "Source ID", "Brand", "Topic ID", "Topic Name"]
            data = [
                [r.id, r.source_id, r.brand, r.topic_id, r.topic_name]
                for r in rows
            ]
            print_table(f"Last {limit} Topic Assignments (topic_results)", headers, data)
            
        else:
            print("Exiting.")

    finally:
        db.close()

if __name__ == "__main__":
    main()
