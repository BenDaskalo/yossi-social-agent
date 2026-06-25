import time
import json
from apify_client import ApifyClient
from memory_manager import save_competitor_data


def scrape_profile(username: str, num_posts: int = 30) -> dict:
    from dotenv import load_dotenv
    import os
    load_dotenv()

    client = ApifyClient(os.getenv("APIFY_API_KEY"))
    print(f"\n🔍 סורק את @{username} ({num_posts} פוסטים)...")

    run = client.actor("apify/instagram-scraper").call(run_input={
        "directUrls": [f"https://www.instagram.com/{username}/"],
        "resultsType": "posts",
        "resultsLimit": num_posts,
        "addParentData": False
    })

    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    print(f"✅ נמשכו {len(items)} פוסטים")
    return items


def analyze_posts(username: str, posts: list) -> dict:
    videos = [p for p in posts if p.get("type") == "Video"]
    sidecars = [p for p in posts if p.get("type") == "Sidecar"]
    images = [p for p in posts if p.get("type") == "Image"]

    all_likes = [p.get("likesCount", 0) for p in posts]
    all_comments = [p.get("commentsCount", 0) for p in posts]

    top_videos = sorted(videos, key=lambda x: x.get("videoViewCount") or 0, reverse=True)[:5]
    top_carousels = sorted(sidecars, key=lambda x: x.get("likesCount", 0), reverse=True)[:5]

    top_hooks = []
    for p in top_videos[:5]:
        caption = (p.get("caption") or "").split("\n")[0][:100]
        top_hooks.append({
            "hook": caption,
            "views": p.get("videoViewCount", 0),
            "likes": p.get("likesCount", 0),
            "duration_sec": p.get("videoDuration", 0),
            "pattern": detect_pattern(caption)
        })

    insights = {
        "followers": posts[0].get("ownerFollowersCount") if posts else 0,
        "total_posts_analyzed": len(posts),
        "avg_likes": round(sum(all_likes) / len(all_likes)) if all_likes else 0,
        "avg_comments": round(sum(all_comments) / len(all_comments), 1) if all_comments else 0,
        "video_count": len(videos),
        "carousel_count": len(sidecars),
        "top_posts": top_hooks,
        "top_carousels": [
            {
                "hook": (p.get("caption") or "").split("\n")[0][:100],
                "likes": p.get("likesCount", 0),
                "comments": p.get("commentsCount", 0)
            }
            for p in top_carousels
        ],
        "key_insight": generate_insight(top_hooks, top_carousels)
    }

    save_competitor_data(username, posts, insights)
    return insights


def detect_pattern(caption: str) -> str:
    caption = caption.lower()
    if any(w in caption for w in ["סוד", "איך", "מה שלא"]):
        return "secret_reveal"
    if any(w in caption for w in ["מישהו אמר", "לא מסכים", "טועים", "לא נכון"]):
        return "myth_bust"
    if any(w in caption for w in ["הסיפור מאחורי", "סיפור"]):
        return "brand_story"
    if any(w in caption for w in ["שאלתם", "שאלו"]):
        return "answer_audience"
    if any(w in caption for w in ["לפני", "שנים", "הדרך שלי"]):
        return "personal_story"
    if any(w in caption for w in ["שלא יעבדו", "זהירות", "טעות"]):
        return "warning"
    return "general"


def generate_insight(top_videos, top_carousels) -> str:
    if not top_videos:
        return "אין מספיק נתונים"
    best = top_videos[0]
    parts = []
    if best.get("duration_sec", 0) < 20:
        parts.append(f"וידאו קצר ({best['duration_sec']:.0f} שניות) עם הוק מסתורי = הכי ויראלי")
    if best.get("views", 0) > 10000:
        parts.append(f"הפוסט הכי חזק הגיע ל-{best['views']:,} צפיות")
    if top_carousels and top_carousels[0].get("likes", 0) > 200:
        parts.append(f"קרוסל מנצח: {top_carousels[0]['likes']} לייקים")
    return " | ".join(parts) if parts else "נדרש ניתוח נוסף"


def print_analysis(username: str, insights: dict):
    print(f"\n{'='*55}")
    print(f"📊 ניתוח @{username}")
    print(f"{'='*55}")
    print(f"עוקבים: {insights.get('followers', '?'):,}")
    print(f"ממוצע לייקים: {insights.get('avg_likes', 0)} | ממוצע תגובות: {insights.get('avg_comments', 0)}")
    print(f"\n🎬 טופ וידאו:")
    for i, p in enumerate(insights.get("top_posts", [])[:3], 1):
        print(f"  [{i}] {p['views']:,} צפיות | {p['likes']} לייקים | {p['duration_sec']:.0f}שנ")
        print(f"      הוק: {p['hook'][:80]}")
    print(f"\n📋 טופ קרוסל:")
    for i, p in enumerate(insights.get("top_carousels", [])[:3], 1):
        print(f"  [{i}] {p['likes']} לייקים | הוק: {p['hook'][:80]}")
    print(f"\n💡 תובנה: {insights.get('key_insight', '')}")
