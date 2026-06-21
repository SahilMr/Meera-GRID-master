import sys
import argparse
from sqlalchemy import inspect, text
from src.db.database import engine

def get_all_tables():
    """Retrieve all table names from the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()

def truncate_table(table_name: str, force: bool = False):
    """
    Truncate/clear all rows from the specified table.
    Handles SQLite vs MySQL/PostgreSQL/other dialects appropriately.
    """
    available_tables = get_all_tables()
    
    if table_name not in available_tables:
        print(f"Error: Table '{table_name}' does not exist in the database.")
        print(f"Available tables: {', '.join(available_tables)}")
        return False

    # Check dialect to decide the truncation query
    dialect_name = engine.dialect.name
    print(f"Detected database dialect: {dialect_name}")

    if not force:
        # Prompt for confirmation
        confirm = input(f"WARNING: Are you sure you want to truncate the table '{table_name}'? All data will be deleted. (y/N): ")
        if confirm.lower() not in ('y', 'yes'):
            print("Operation cancelled.")
            return False

    try:
        with engine.begin() as connection:
            if dialect_name == "sqlite":
                # SQLite does not support TRUNCATE, so we use DELETE
                # Disable foreign key checks temporarily if needed, or delete directly
                print(f"Truncating table '{table_name}' (deleting all records)...")
                connection.execute(text(f"DELETE FROM {table_name}"))
                
                # Check if sqlite_sequence table exists to reset AUTOINCREMENT counters
                seq_check = connection.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'")
                ).fetchone()
                if seq_check:
                    connection.execute(
                        text("DELETE FROM sqlite_sequence WHERE name = :table"),
                        {"table": table_name}
                    )
                
                # Run vacuum to reclaim space (optional but good practice for SQLite)
                # Note: VACUUM cannot be run inside a transaction block in SQLite, so we run it outside if needed,
                # but we'll skip it or run it on the connection if not in a transaction.
                # connection.execute(text("VACUUM"))
            else:
                # PostgreSQL, MySQL, MSSQL, Oracle, etc.
                # Use CASCADE to handle foreign keys if foreign key checks are enabled.
                print(f"Truncating table '{table_name}'...")
                if dialect_name == "postgresql":
                    connection.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
                else:
                    # Generic TRUNCATE statement
                    connection.execute(text(f"TRUNCATE TABLE {table_name}"))

        print(f"Successfully truncated table '{table_name}'.")
        return True
    except Exception as e:
        print(f"An error occurred while truncating table '{table_name}': {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Truncate a table in the database.")
    parser.add_argument(
        "table", 
        nargs="?", 
        help="Name of the table to truncate. If not provided, you will be prompted to choose from a list."
    )
    parser.add_argument(
        "-f", "--force", 
        action="store_true", 
        help="Skip the confirmation prompt."
    )
    args = parser.parse_args()

    tables = get_all_tables()
    if not tables:
        print("No tables found in the database.")
        sys.exit(0)

    selected_table = args.table

    if not selected_table:
        print("Available tables in the database:")
        for idx, table in enumerate(tables, 1):
            print(f"  {idx}. {table}")
        
        try:
            choice = input("\nEnter the number or name of the table to truncate (or press Enter to cancel): ").strip()
            if not choice:
                print("No table selected. Exiting.")
                sys.exit(0)
            
            # Check if choice is a number
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(tables):
                    selected_table = tables[choice_idx]
                else:
                    print("Invalid index choice.")
                    sys.exit(1)
            else:
                selected_table = choice
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

    success = truncate_table(selected_table, force=args.force)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
