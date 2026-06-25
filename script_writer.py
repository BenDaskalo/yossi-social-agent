import anthropic
import os
from memory_manager import build_system_prompt, save_script, get_competitor_insights


def generate_script(topic: str, pattern: str = None) -> dict:
    from dotenv import load_dotenv
    load_dotenv()

    insights = get_competitor_insights()
    patterns = insights.get("winning_patterns", [])
    pattern_info = next((p for p in patterns if p["name"] == pattern), None)

    pattern_instruction = ""
    if pattern_info:
        pattern_instruction = f"\nהשתמש בדפוס: {pattern_info['name']} — {pattern_info['description']}\nדוגמה: \"{pattern_info.get('example', '')}\""

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    system = build_system_prompt()

    user_prompt = f"""כתוב תסריט מלא לסרטון אינסטגרם על הנושא: {topic}
{pattern_instruction}

המבנה:
1. [HOOK — 0-3 שניות] — עוצר גלילה, מספר ספציפי או שאלה שפונה ישירות לצופה
2. [הבעיה — 3-15 שניות] — הכאב שהצופה מרגיש
3. [הסיפור — 15-40 שניות] — דוגמה אמיתית, ספציפית, עם תוצאה
4. [הערך — 40-60 שניות] — למה זה קורה, מה השיעור
5. [CTA — 60-75 שניות] — פעולה ספציפית אחת

חשוב:
- הסיפור תמיד מנקודת מבט הלקוח שמקבל את התוצאה
- מספרים ספציפיים
- ישיר ושקוף, לא מוכר
- עברית בלבד

החזר:
HOOK: [הוק בלבד]
---
SCRIPT: [התסריט המלא]"""

    print("\n✍️ כותב תסריט...")
    response = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        max_tokens=1500,
        messages=[{"role": "user", "content": user_prompt}],
        system=system
    )

    content = response.content[0].text
    hook = ""
    script = content

    if "HOOK:" in content and "SCRIPT:" in content:
        parts = content.split("---")
        hook_part = parts[0].replace("HOOK:", "").strip()
        script_part = parts[1].replace("SCRIPT:", "").strip() if len(parts) > 1 else content
        hook = hook_part
        script = script_part
    else:
        lines = content.split("\n")
        hook = lines[0].strip()
        script = content

    script_id = save_script(topic, hook, script)
    return {"id": script_id, "hook": hook, "script": script}


def improve_script(script_id: int, feedback: str) -> dict:
    from dotenv import load_dotenv
    from memory_manager import get_approved_scripts, save, save_correction
    load_dotenv()

    data = get_approved_scripts()
    original = next((s for s in data.get("scripts", []) if s["id"] == script_id), None)
    if not original:
        print("❌ תסריט לא נמצא")
        return {}

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""התסריט המקורי:
{original['full_script']}

הפידבק של יוסי:
{feedback}

שפר את התסריט לפי הפידבק. שמור על אותו מבנה אבל תקן מה שצריך.
עברית בלבד."""

    response = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
        system=build_system_prompt()
    )

    improved = response.content[0].text

    save_correction(
        wrong=f"גרסה {script_id} המקורית",
        correct=f"גרסה משופרת לפי: {feedback}",
        rule=feedback,
        context=f"שיפור תסריט #{script_id}"
    )

    new_id = save_script(
        original["topic"],
        original["hook"],
        improved,
        status="pending"
    )

    return {"id": new_id, "script": improved}
