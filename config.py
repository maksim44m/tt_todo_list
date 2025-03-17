from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
UTILS_DIR = BASE_DIR / "utils"

sqlite_url = f'sqlite:///{DATABASE_DIR / "data.db"}'
