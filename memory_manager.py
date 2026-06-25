import json
import os
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path(__file__).parent / "memory"

def load(filename):
    path = MEMORY_DIR / filename
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save(filename, data):
    path = MEMORY_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_profile():
    return load("profile.json")

def get_feedback():
    return load("feedback.json")

def get_approved_scripts():
    return load("approved_scripts.json")

def get_competitor_insights():
    return load("competitor_insights.json")

def save_correction(wrong, correct, rule, context=""):
    feedback = get_feedback()
    feedback.setdefault("corrections", []).append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "context": context,
        "wrong": wrong,
        "correct": correct,
        "rule": rule
    })
    save("feedback.json", feedback)
    print(f"\n✅ למידה נשמרה: {rule}\n")

def save_style_rule(rule):
    feedback = get_feedback()
    rules = feedback.setdefault("style_rules", [])
    if rule not in rules:
        rules.append(rule)
        save("feedback.json", feedback)
        print(f"\n✅ כלל סגנון נשמר: {rule}\n")

def approve_script(script_id):
    data = get_approved_scripts()
    for s in data.get("scripts", []):
        if s["id"] == script_id:
            s["status"] = "approved"
    save("approved_scripts.json", data)

def save_script(topic, hook, full_script, status="pending", duration="60-90 שניות"):
    data = get_approved_scripts()
    scripts = data.setdefault("scripts", [])
    new_id = max([s.get("id", 0) for s in scripts], default=0) + 1
    scripts.append({
        "id": new_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "topic": topic,
        "hook": hook,
        "full_script": full_script,
        "status": status,
        "duration_estimate": duration,
        "format": "דיבור למצלמה"
    })
    save("approved_scripts.json", data)
    return new_id

def save_competitor_data(username, posts_data, insights):
    data = get_competitor_insights()
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    accounts = data.setdefault("accounts_analyzed", [])
    existing = next((a for a in accounts if a["username"] == username), None)
    if existing:
        existing.update(insights)
    else:
        accounts.append({"username": username, **insights})
    save("competitor_insights.json", data)

def build_system_prompt():
    profile = get_profile()
    feedback = get_feedback()
    scripts = get_approved_scripts()
    insights = get_competitor_insights()

    approved = [s for s in scripts.get("scripts", []) if s.get("status") == "approved"]
    examples = "\n\n".join([
        f'דוגמה מאושרת #{s["id"]}:\nהוק: {s["hook"]}\nתסריט: {s["full_script"][:300]}...'
        for s in approved[-3:]
    ]) if approved else "אין עדיין תסריטים מאושרים"

    corrections = feedback.get("corrections", [])
    correction_text = "\n".join([
        f'❌ לא: "{c["wrong"]}" → ✅ כן: "{c["correct"]}" | כלל: {c["rule"]}'
        for c in corrections
    ]) if corrections else "אין עדיין תיקונים"

    style_rules = "\n".join([f"• {r}" for r in feedback.get("style_rules", [])])

    winning = insights.get("winning_patterns", [])
    patterns_text = "\n".join([
        f'• {p["name"]}: {p["description"]} (דוגמה: "{p.get("example","")}")'
        for p in winning
    ])

    return f"""אתה מנהל הסושיאל האישי של {profile.get('name', 'יוסי')}.

## פרופיל
- תחום: {profile.get('niche')}
- רקע: {profile.get('background')}
- קהל יעד: {profile.get('target_audience')}
- ערך ייחודי: {profile.get('unique_value')}
- סגנון: {profile.get('content_style', {}).get('tone')}
- גישה: {profile.get('content_style', {}).get('approach')}
- פילוסופיה: {profile.get('content_style', {}).get('philosophy')}
- שפה: {profile.get('language')}

## כללי תוכן
{chr(10).join(['• ' + r for r in profile.get('content_rules', [])])}

## כללי סגנון שנלמדו
{style_rules}

## טעויות שנלמדו — לא לחזור עליהן
{correction_text}

## דפוסי תוכן מנצחים (מחקר מתחרים)
{patterns_text}

## תסריטים מאושרים — ללמוד מהם
{examples}

## חוקים חשובים
- תמיד עברית בלבד
- שאלה אחת בכל פעם
- הסיפור תמיד מנקודת מבט הלקוח שמקבל ערך — לא של יוסי
- לא לכתוב תוכן שנשמע כמו מכירה
- כשיוסי מתקן אותך — שאל אם לשמור את זה כלמידה"""
