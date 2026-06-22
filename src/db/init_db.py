from src.db.database import Base, engine, SessionLocal
# Import all models to ensure they are registered on Base.metadata
from src.db.models import (
    StatusLookup, RtiQuery, SupportingDocument, OfficeNote,
    UserQuery, UserQuerySource, AssistantSuggestion, SuggestionSource,
    DepartmentMappingMaster
)

def migrate_columns():
    import sqlite3
    from src.db.database import DATABASE_URL
    if DATABASE_URL.startswith("sqlite"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        if "?" in db_path:
            db_path = db_path.split("?")[0]
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rti_query';")
            if cur.fetchone():
                cur.execute("PRAGMA table_info(rti_query);")
                existing_cols = [col[1] for col in cur.fetchall()]
                
                new_cols = {
                    "inward_id": "VARCHAR(100)",
                    "query_text": "VARCHAR",
                    "department_id": "INTEGER",
                    "assigned_to": "VARCHAR(100)",
                    "assigned_at": "VARCHAR(50)"
                }
                
                for col_name, col_type in new_cols.items():
                    if col_name not in existing_cols:
                        cur.execute(f"ALTER TABLE rti_query ADD COLUMN {col_name} {col_type};")
                        print(f"Migration: Added column {col_name} to rti_query table.")
                conn.commit()
        except Exception as e:
            print(f"Error during SQLite auto-migration: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

def init_db():
    # Run auto-migration for existing SQLite database
    # migrate_columns()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Seed initial data
    db = SessionLocal()
    try:
        # Seed default statuses if they don't exist
        default_statuses = [
            (1, "Pending"),
            (2, "In Progress"),
            (3, "Resolved"),
            (4, "Not In Scope"),
            (5, "Needs Revision"),
        ]
        for sid, label in default_statuses:
            status_obj = db.query(StatusLookup).filter(StatusLookup.status_id == sid).first()
            if not status_obj:
                db.add(StatusLookup(status_id=sid, status_label=label))
        db.commit()
        print("Status lookup table seeded/verified successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
