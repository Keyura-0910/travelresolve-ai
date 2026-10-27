"""
Script to initialize SQLite database tables and seed synthetic travel records.
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database import init_db, SessionLocal
from app.seed_data import generate_seed_data


def main():
    print("Initializing SQLite database tables...")
    init_db()
    with SessionLocal() as db:
        stats = generate_seed_data(db)
        print(f"Database successfully initialized with synthetic records: {stats}")


if __name__ == "__main__":
    main()
