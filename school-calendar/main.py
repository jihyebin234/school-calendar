from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def main():
    print("school-calendar")
    print("DB:", (BASE_DIR / "school_calendar.db").absolute())


if __name__ == "__main__":
    main()
