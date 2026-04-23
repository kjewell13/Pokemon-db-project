from app.app import app
from services.import_service import main


if __name__ == "__main__":
    with app.app_context():
        main()