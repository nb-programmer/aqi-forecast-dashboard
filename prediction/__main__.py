
from prediction import init_app
import os

if __name__ == "__main__":
    DEBUG = bool(os.environ.get("DEBUG", "0"))
    app = init_app(DEBUG)
    app.run(host='0.0.0.0', port=5000, load_dotenv=True, debug=DEBUG)
