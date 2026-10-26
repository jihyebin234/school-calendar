from database import init_db
from ui.main_window import main as run_ui


def main():
    init_db()
    run_ui()


if __name__ == "__main__":
    main()
