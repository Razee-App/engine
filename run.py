from flask import Flask
from config.config import Config
from app.ocr_service import ocr_blueprint
from app.video_service import video_blueprint
from app.document_service import document_blueprint
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from Config class

# Print configuration values
print("Configuration Loaded:")
print(Config())

app.register_blueprint(ocr_blueprint, url_prefix='/api')
app.register_blueprint(video_blueprint, url_prefix='/api')
app.register_blueprint(document_blueprint, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
