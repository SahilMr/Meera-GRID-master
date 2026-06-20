from src.db.database import Base, engine, SessionLocal
# Import all models to ensure they are registered on Base.metadata
from src.db.models import (
    StatusLookup, RtiQuery, SupportingDocument, OfficeNote,
    UserQuery, UserQuerySource, AssistantSuggestion, SuggestionSource,
    DepartmentMappingMaster
)

def init_db():
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
            (4, "Not In Scope")
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
