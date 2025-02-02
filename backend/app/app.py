from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from app import api
import os

app = Flask(__name__)

# Mount static files
app.static_folder = 'frontend'

# Register blueprints
app.register_blueprint(api.bp)

# Swagger UI setup
SWAGGER_URL = '/swagger'
API_URL = '/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Hotel Booking API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend'))

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory(frontend_dir, path)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)