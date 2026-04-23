from app.app import app
from services.import_prices_service import main

if __name__ == "__main__":
    with app.app_context():
        main()