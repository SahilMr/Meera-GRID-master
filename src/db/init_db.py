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
        # Check if status lookup is empty
        if db.query(StatusLookup).count() == 0:
            default_statuses = [
                StatusLookup(status_id=1, status_label="Pending"),
                StatusLookup(status_id=2, status_label="In Progress"),
                StatusLookup(status_id=3, status_label="Resolved")
            ]
            db.add_all(default_statuses)
            db.commit()
            print("Status lookup table seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
