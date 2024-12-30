# src/summary/summarizer.py

import os
import json
from datetime import datetime
import textwrap
import openai
from dotenv import load_dotenv

load_dotenv()

def generate_post_summary(posts, ticker, api_key=None):
    """
    Summarize forum posts using OpenAI. Weighted by newer posts and certain authors,
    but do not explicitly mention authors or 'posts'.
    """
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = api_key

    # Sort posts newest first
    sorted_posts = sorted(posts, key=lambda x: x['timestamp'], reverse=True)

    # Build system + user prompt
    system_prompt = (
        "You are a helpful assistant that produces direct, factual summaries. "
        "Follow the exact formatting requirements: numbered bullet points, no mention of authors.\n"
    )
    user_intro = f"""
    Summarize key insights about {ticker} in concise bullet points (no more than 10).
    Give more weight to newer info and to content from "smgacm@gmail.com," 
    but do not mention authors or 'posts' in your summary.
    Present the summary directly as bullet points without referencing messages.

    Format:
    - No title.
    - Numbered bullet points, each bullet has a bold introduction.

    ---
    Here are the messages (newest first):
    """

    messages_str = ""
    for p in sorted_posts:
        dt = datetime.fromtimestamp(p["timestamp"])
        snippet = f"Date: {dt}\nMessage:\n{p['message']}\n\n"
        messages_str += snippet

    user_prompt = user_intro + messages_str

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI summarization error: {e}")
        return "No forum summary available."

def summarize_ticker_posts(ticker, output_dir="output", api_key=None):
    """
    Load {ticker}_posts.json, generate summary, save to {ticker}_post_summary.txt.
    """
    posts_file = os.path.join(output_dir, f"{ticker}_posts.json")
    if not os.path.exists(posts_file):
        print(f"Posts file '{posts_file}' not found.")
        return "No forum summary available."

    with open(posts_file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    summary = generate_post_summary(posts, ticker, api_key=api_key)

    out_file = os.path.join(output_dir, f"{ticker}_post_summary.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary for {ticker} written to '{out_file}'.")
    return summary
