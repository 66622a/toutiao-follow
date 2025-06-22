# Toutiao Follow

This small project fetches feed data from Toutiao and displays it in a simple web page.

## Usage

1. Open `index.html` directly in your browser. It will request data from
   `https://toutiao-api.11451499.xyz/api/feed` by default.

2. If you prefer to run the backend locally, install the dependencies and start
   the Flask server:
   ```bash
   pip install Flask Flask-Cors requests cachetools
   python backend.py
   ```
Then change the `API_URL` in `index.html` to `/api/feed` so it fetches from
the local server on port `5000`.

3. Use the moon icon in the header to switch between light and dark modes.
   Your preference is stored locally so the next visit keeps the same theme.
