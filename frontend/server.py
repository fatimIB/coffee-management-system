from flask import Flask, send_from_directory, abort
import os

app = Flask(__name__, static_folder='.')

# Serve the main page (default to login)
@app.route('/')
def home():
    return send_from_directory('login', 'index.html')

# Dynamically serve any page with /<folder>/index.html
@app.route('/<folder>/index.html')
def serve_page(folder):
    folder_path = os.path.join(app.static_folder, folder)
    if os.path.exists(os.path.join(folder_path, 'index.html')):
        return send_from_directory(folder, 'index.html')
    else:
        abort(404)

# Serve static files (CSS/JS/images) dynamically
@app.route('/<folder>/<filename>')
def serve_static(folder, filename):
    file_path = os.path.join(app.static_folder, folder, filename)
    if os.path.exists(file_path):
        return send_from_directory(folder, filename)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
