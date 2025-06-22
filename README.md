# Toutiao Follow

This small project fetches feed data from Toutiao and displays it in a simple web page.

## Usage

1. Install dependencies and start the backend:
   ```bash
   pip install Flask Flask-Cors requests cachetools
   python backend.py
   ```
   The Flask server will listen on port `5000`.

2. Open `index.html` in your browser. The page uses the relative URL `/api/feed` so it works with the local backend by default. Ensure the backend is running on the same host and port (e.g. `http://localhost:5000/api/feed`).

3. If you need to fetch from a different endpoint, edit the `API_URL` constant in `index.html`.
