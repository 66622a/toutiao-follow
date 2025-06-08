# backend.py
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime
import time

# --- Create the Flask App ---
app = Flask(__name__)
# Enable CORS to allow requests from any origin. For production, you'd restrict this.
CORS(app) 

# --- Your Existing Toutiao Fetching Logic ---
# (Slightly modified to be a reusable function)

def fetch_toutiao_data():
    main_feed_url = "https://www.toutiao.com/api/pc/list/user/feed?category=pc_profile_ugc&token=MS4wLjABAAAAfuLrCjbbZL8H-LNXIuUpmNY8akAjw1dyvywVOW6ARDg&max_behot_time=0&entrance_gid=&aid=24&app_name=toutiao_web&a_bogus=dy8MMmgDDEdkkf6d5WOLfY3qVWq3YMHr0t9bMDhqGVfevg39HMO99exE9UzvNpWjxG%2FZIeLjy4hSOpPMiOC7A3v6HSRKl2Ck-g00t-PZ5o0j5ZvruyR0rtRF4kt4FeeM5iQ3xOssy7QtKSRmW9Pe-wHvPjojx2f39gbs"
    comments_base_url = "https://www.toutiao.com/article/v4/tab_comments/?aid=24&app_name=toutiao_web&offset=0&count=20&group_id={article_id}&item_id={article_id}&_signature=_02B4Z6wo00f010FByBQAAIDA7QLqc7YuVj9BZcyAALgggUHgqPh4-oiMoBeqGn1MtpaTNpd07FLxDtj6Dn1IKLfU3JXAw6od8sYMJPRxLB2l3E0tYr02tImAqjeWRvPT3JnGuiZq0o8zCOXC77"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    all_extracted_data = []

    try:
        # First API Call: Get user feed articles
        print("Fetching main feed data from Toutiao...")
        feed_response = requests.get(main_feed_url, headers=headers)
        feed_response.raise_for_status()
        feed_data = feed_response.json()

        if feed_data and "data" in feed_data:
            for item in feed_data["data"]:
                article_info = {
                    "id": item.get("thread_id") or item.get("id"),
                    "content": item.get("content"),
                    "create_time": datetime.fromtimestamp(item.get("create_time")).strftime('%Y-%m-%d %H:%M:%S') if item.get("create_time") else None,
                    "comments": []
                }

                # Second API Call: Get comments
                if article_info["id"]:
                    comments_url = comments_base_url.format(article_id=article_info["id"])
                    print(f"  Fetching comments for article ID: {article_info['id']}")
                    try:
                        comments_response = requests.get(comments_url, headers=headers)
                        comments_response.raise_for_status()
                        comments_data = comments_response.json()

                        if comments_data and "data" in comments_data:
                            for comment_entry in comments_data["data"]:
                                comment_data = {
                                    "text": comment_entry.get("comment", {}).get("text"),
                                    "user_name": comment_entry.get("comment", {}).get("user_name"),
                                    "ip_location": comment_entry.get("comment", {}).get("publish_loc_info")
                                }
                                article_info["comments"].append(comment_data)
                    except Exception as e:
                        print(f"    Error fetching comments for {article_info['id']}: {e}")
                    
                    time.sleep(0.2) # Small delay

                all_extracted_data.append(article_info)
        return all_extracted_data

    except Exception as e:
        print(f"An error occurred while fetching the main feed: {e}")
        return {"error": str(e)}, 500


# --- Define the API Endpoint ---
@app.route('/api/feed', methods=['GET'])
def get_feed_data():
    print("Request received at /api/feed")
    data = fetch_toutiao_data()
    # jsonify converts the Python dictionary (or list) to a JSON response
    return jsonify(data) 

# --- Run the Server ---
if __name__ == '__main__':
    # Runs the server on http://localhost:5000
    # debug=True allows the server to auto-reload when you save the file
    app.run(port=5000, debug=True)
