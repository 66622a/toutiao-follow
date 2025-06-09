# backend.py (版本 5.1 - 修正了API请求URL)

# 确保已安装: pip install Flask Flask-Cors requests cachetools
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime
import time
from cachetools import cached, TTLCache

# --- Create the Flask App ---
app = Flask(__name__)
CORS(app) 

# --- 缓存设置 ---
cache = TTLCache(maxsize=1, ttl=600)

# --- 数据获取函数 ---
@cached(cache)
def fetch_toutiao_data():
    """
    智能识别转发动态，并用原文的标题和描述重组内容，提供更丰富的上下文。
    """
    print("后端日志: 缓存未命中或已过期，正在执行实时API请求从头条获取新数据...")
    
    # --- API URL 定义 ---
    # 【修正】已将 a_bogus 等完整参数加回到所有URL中
    feed_url_ugc = "https://www.toutiao.com/api/pc/list/user/feed?category=pc_profile_ugc&token=MS4wLjABAAAAfuLrCjbbZL8H-LNXIuUpmNY8akAjw1dyvywVOW6ARDg&max_behot_time=0&entrance_gid=&aid=24&app_name=toutiao_web&a_bogus=dy8MMmgDDEdkkf6d5WOLfY3qVWq3YMHr0t9bMDhqGVfevg39HMO99exE9UzvNpWjxG%2FZIeLjy4hSOpPMiOC7A3v6HSRKl2Ck-g00t-PZ5o0j5ZvruyR0rtRF4kt4FeeM5iQ3xOssy7QtKSRmW9Pe-wHvPjojx2f39gbs"
    comments_url_ugc = "https://www.toutiao.com/article/v4/tab_comments/?aid=24&app_name=toutiao_web&offset=0&count=20&group_id={article_id}&item_id={article_id}&_signature=_02B4Z6wo00f010FByBQAAIDA7QLqc7YuVj9BZcyAALgggUHgqPh4-oiMoBeqGn1MtpaTNpd07FLxDtj6Dn1IKLfU3JXAw6od8sYMJPRxLB2l3E0tYr02tImAqjeWRvPT3JnGuiZq0o8zCOXC77"
    
    feed_url_all = "https://www.toutiao.com/api/pc/list/user/feed?category=profile_all&token=MS4wLjABAAAAfuLrCjbbZL8H-LNXIuUpmNY8akAjw1dyvywVOW6ARDg&max_behot_time=0&entrance_gid=&aid=24&app_name=toutiao_web&a_bogus=x780BdgvdkIkhVW25U5LfY3qV3e3YM9C0t9bMDhqsnfen639HMPs9exEJ44vD66jxG%2FZIeLjy4hJY3MMiOC7A3v6HSRKl2Ck-g00t-PZ5o0j5ZvruyR0rtRF4kt4FeeM5iQ3xOssy7CaKuRmW9Pe-wHvPjojx2f39gbj"
    comments_url_reply = "https://www.toutiao.com/2/comment/v4/reply_list/?aid=24&app_name=toutiao_web&id={id}&offset=0&count=20&repost=1&_signature=_02B4Z6wo00d01MpP3SAAAIDDZgz.R1WEOiDKa9mAAFrbNULNMNq9Q8jM7Voi4R.wBa6shcOHbMki9u.MXoc3TAOJSteoaWa7Enj6dTDam.BOkL0os2I7j6IKS9zBM.AJoAMU0nqhXwHSr5Ilbf"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    all_extracted_data = []
    processed_ids = set()

    try:
        # --- Phase 1: 处理 UGC Feed (源1) ---
        print("后端日志: 正在处理 UGC Feed (源1)...")
        feed_response_ugc = requests.get(feed_url_ugc, headers=headers, timeout=10)
        feed_response_ugc.raise_for_status()
        feed_data_ugc = feed_response_ugc.json() # 现在这一步应该可以成功了
        if feed_data_ugc and "data" in feed_data_ugc:
            for item in feed_data_ugc["data"]:
                article_id = item.get("thread_id") or item.get("id")
                if not article_id or article_id in processed_ids: continue
                article_info = {
                    "id": article_id, "content": item.get("content"),
                    "create_time": datetime.fromtimestamp(item.get("create_time")).strftime('%Y-%m-%d %H:%M:%S') if item.get("create_time") else None,
                    "comments": []
                }
                comments_url = comments_url_ugc.format(article_id=article_info["id"])
                try:
                    comments_response = requests.get(comments_url, headers=headers, timeout=10)
                    comments_response.raise_for_status()
                    comments_data = comments_response.json()
                    if comments_data and "data" in comments_data:
                        article_info["comments"] = [{"text": c.get("comment", {}).get("text"),"user_name": c.get("comment", {}).get("user_name"),"ip_location": c.get("comment", {}).get("publish_loc_info")} for c in comments_data["data"]]
                except requests.exceptions.RequestException as e:
                    print(f"后端日志警告: 获取UGC文章 {article_info['id']} 的评论失败: {e}")
                all_extracted_data.append(article_info)
                processed_ids.add(article_id)
                time.sleep(0.2)
        
        # --- Phase 2: 处理 Profile All Feed (源2) ---
        print("后端日志: 正在处理 Profile All Feed (源2) 并智能重组内容...")
        feed_response_all = requests.get(feed_url_all, headers=headers, timeout=10)
        feed_response_all.raise_for_status()
        feed_data_all = feed_response_all.json()

        if feed_data_all and "data" in feed_data_all:
            for item in feed_data_all["data"]:
                comment_base = item.get("comment_base", {})
                article_id = comment_base.get("id")
                if not article_id or article_id in processed_ids:
                    continue
                
                final_content = ""
                if "origin_thread" in item and item["origin_thread"]:
                    print(f"后端日志: 检测到转发动态 (ID: {article_id}), 正在进行内容重组。")
                    origin_thread = item.get("origin_thread", {})
                    share_info = origin_thread.get("itemCell", {}).get("shareInfo", {})
                    title = share_info.get("title", "")
                    description = share_info.get("description", "")
                    user_comment = comment_base.get("content", "")
                    final_content = f"{title}\n\n{description}\n\n---\n{user_comment}".strip()
                else:
                    final_content = comment_base.get("content", "")

                article_info = {
                    "id": article_id, "content": final_content,
                    "create_time": datetime.fromtimestamp(comment_base.get("create_time")).strftime('%Y-%m-%d %H:%M:%S') if comment_base.get("create_time") else None,
                    "comments": []
                }
                
                comments_url = comments_url_reply.format(id=article_info["id"])
                try:
                    comments_response = requests.get(comments_url, headers=headers, timeout=10)
                    comments_response.raise_for_status()
                    comments_data = comments_response.json()
                    if comments_data and comments_data.get("data", {}).get("data"):
                        article_info["comments"] = [{"text": c.get("content"),"user_name": c.get("user", {}).get("name"),"ip_location": c.get("publish_loc_info")} for c in comments_data["data"]["data"]]
                except requests.exceptions.RequestException as e:
                    print(f"后端日志警告: 获取Profile文章 {article_info['id']} 的评论失败: {e}")
                
                all_extracted_data.append(article_info)
                processed_ids.add(article_id)
                time.sleep(0.2)

        # --- Phase 3: 排序 ---
        all_extracted_data.sort(key=lambda x: x['create_time'] or '0', reverse=True)

        print(f"后端日志: 新数据获取并处理完成。共聚合 {len(all_extracted_data)} 条动态。结果将被缓存。")
        return {"data": all_extracted_data, "error": None}

    except requests.exceptions.RequestException as e:
        print(f"后端日志错误: 请求主Feed时发生致命错误: {e}")
        return {"data": None, "error": f"无法从头条服务器获取数据: {e}"}
    except Exception as e:
        print(f"后端日志错误: 发生未知错误: {e}")
        return {"data": None, "error": f"后端发生未知错误: {e}"}

# --- API Endpoint ---
@app.route('/api/feed', methods=['GET'])
def get_feed_data():
    print("\n后端日志: 前端请求已到达 /api/feed")
    result = fetch_toutiao_data()
    if result["error"]:
        return jsonify({"error": result["error"]}), 500
    print("后端日志: 正在向前端返回数据 (可能来自缓存或实时请求)。")
    return jsonify(result["data"])

# --- Run the Server ---
if __name__ == '__main__':
    app.run(port=5000, debug=True)
