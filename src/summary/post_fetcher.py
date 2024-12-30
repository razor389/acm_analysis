# src/summary/post_fetcher.py

import os
import json
import requests
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)  # create a module-level logger

class WebsiteToolboxFetcher:
    def __init__(self, api_key: str, base_url: str = "https://api.websitetoolbox.com/v1/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "x-api-key": self.api_key
        })
        logger.debug(f"Initialized WebsiteToolboxFetcher with base_url={self.base_url}")

    def get_categories(self):
        url = f"{self.base_url}/categories"
        logger.debug(f"Requesting categories from {url}")
        resp = self.session.get(url)
        logger.debug(f"Response status code: {resp.status_code}")
        resp.raise_for_status()
        return resp.json()

    def get_topics_for_category(self, category_id: str):
        url = f"{self.base_url}/topics"
        logger.debug(f"Fetching topics for category {category_id} from {url}")
        resp = self.session.get(url, params={"categoryId": category_id})
        logger.debug(f"Response status code: {resp.status_code}")
        resp.raise_for_status()
        return resp.json()

    def get_posts_for_topic(self, topic_id: str):
        url = f"{self.base_url}/posts"
        logger.debug(f"Fetching posts for topic {topic_id} from {url}")
        resp = self.session.get(url, params={"topicId": topic_id})
        logger.debug(f"Response status code: {resp.status_code}")
        resp.raise_for_status()
        return resp.json()

    def find_category_by_title(self, title: str):
        logger.debug(f"Looking for category with title '{title}'")
        all_cats = self.get_categories()
        for cat in all_cats.get("data", []):
            if cat.get("title") == title:
                logger.debug(f"Found matching category: {cat}")
                return cat
        logger.debug(f"No matching category found for title '{title}'")
        return None

    def get_subcategories(self, all_categories, parent_id: str):
        logger.debug(f"Finding subcategories under parent_id={parent_id}")
        subcats = []
        for cat in all_categories.get("data", []):
            if cat.get("parentId") == parent_id:
                logger.debug(f"Found subcategory: {cat}")
                subcats.append(cat)
                subcats += self.get_subcategories(all_categories, cat["categoryId"])
        return subcats


def fetch_all_posts_for_ticker(ticker: str, output_dir: str, api_key: str):
    logger.info(f"Fetching all posts for ticker '{ticker}'...")
    fetcher = WebsiteToolboxFetcher(api_key=api_key)

    # 1) Get all categories
    all_cats = fetcher.get_categories()
    cat_list = all_cats.get("data", [])
    if not cat_list:
        logger.warning("No categories returned from the API.")
        return

    # 2) Find parent category
    parent_cat = fetcher.find_category_by_title(ticker)
    if not parent_cat:
        logger.warning(f"No category found with title '{ticker}'.")
        return

    parent_id = parent_cat["categoryId"]
    logger.debug(f"Found category '{ticker}' (ID={parent_id}).")

    # 3) Get subcategories
    subcategories = fetcher.get_subcategories(all_cats, parent_id)
    logger.debug(f"Found {len(subcategories)} subcategories under '{ticker}'.")

    relevant_cats = [parent_cat] + subcategories
    unique_posts = {}

    # 4) For each category, fetch topics -> posts
    for cat in relevant_cats:
        cat_id = cat["categoryId"]
        cat_title = cat["title"]

        topics_data = fetcher.get_topics_for_category(cat_id)
        topics_list = topics_data.get("data", [])

        logger.debug(f"Category '{cat_title}' (ID={cat_id}) -> {len(topics_list)} topic(s).")

        for topic in topics_list:
            topic_id = topic.get("topicId")
            topic_title = topic.get("title")

            posts_data = fetcher.get_posts_for_topic(topic_id)
            posts_list = posts_data.get("data", [])

            logger.debug(f"  Topic '{topic_title}' (ID={topic_id}) -> {len(posts_list)} post(s).")

            for post in posts_list:
                p_id = post.get("postId")
                if p_id not in unique_posts:
                    unique_posts[p_id] = post

    # 5) Simplify & clean each post
    simplified_posts = []
    for post_id, post in unique_posts.items():
        raw_html = post.get("message", "")
        soup = BeautifulSoup(raw_html, "html.parser")
        clean_msg = soup.get_text(separator=" ").strip()
        author_email = post.get("author", {}).get("email", "")

        simplified_posts.append({
            "postId": post_id,
            "timestamp": post.get("postTimestamp", 0),
            "message": clean_msg,
            "authorEmail": author_email
        })

    # 6) Sort by timestamp ascending
    simplified_posts.sort(key=lambda p: p["timestamp"])

    # 7) Save
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, f"{ticker}_posts.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(simplified_posts, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(simplified_posts)} posts to '{out_file}'.")
    return simplified_posts
