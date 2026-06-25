#!/usr/bin/env python3
"""
Yossi Social Agent — מנהל הסושיאל האישי של יוסי אליהו
"""

import os
import sys
import anthropic
from dotenv import load_dotenv
from memory_manager import (
    build_system_prompt, get_approved_scripts,
    save_correction, save_style_rule, approve_script, get_feedback
)
from scraper import scrape_profile, analyze_posts, print_analysis
from script_writer import generate_script, improve_script

load_dotenv()

COMMANDS = """
פקודות זמינות:
  סרטון <נושא>         — כתוב תסריט חדש
  סרטון <נושא> --דפוס <שם>  — כתוב עם דפוס ספציפי (mystery_short, myth_bust, big_brand_story, personal_story)
  סרוק <username>       — נתח מתחרה באינסטגרם
  אשר <מספר>           — אשר תסריט כמאושר (לומד ממנו)
  שפר <מספר>           — שפר תסריט לפי פידבק
  למד <טעות> | <נכון>   — שמור תיקון ידני
  כלל <כלל סגנון>      — שמור כלל סגנון
  תסריטים              — הצג כל התסריטים
  פידבק                — הצג את כל מה שנלמד
  עזרה                 — הצג פקודות
  יציאה                — סגור
"""

def print_banner():
    print("\n" + "="*55)
    print("   🎬 יוסי סושיאל אייג'נט")
    print("   מנהל תוכן אישי עם זיכרון ולמידה עצמית")
    print("="*55)
    print(COMMANDS)

def handle_command(user_input: str, conversation_history: list) -> str:
    cmd = user_input.strip()

    if cmd.startswith("סרטון "):
        parts = cmd[6:].strip()
        pattern = None
        if "--דפוס" in parts:
            topic, pat = parts.split("--דפוס")
            pattern = pat.strip()
            parts = topic.strip()
        result = generate_script(parts, pattern)
        print(f"\n{'='*55}")
        print(f"📝 תסריט #{result['id']}")
        print(f"{'='*55}")
        print(f"\n🎯 HOOK:\n{result['hook']}")
        print(f"\n📜 תסריט מלא:\n{result['script']}")
        print(f"\n{'='*55}")
        print("➡️  כתוב 'אשר {}'.format(result['id']) לאישור, או 'שפר {}' לשיפור".format(result['id'], result['id']))
        return ""

    if cmd.startswith("סרוק "):
        username = cmd[5:].strip().lstrip("@")
        posts = scrape_profile(username, num_posts=30)
        insights = analyze_posts(username, posts)
        print_analysis(username, insights)
        return ""

    if cmd.startswith("אשר "):
        script_id = int(cmd[4:].strip())
        approve_script(script_id)
        print(f"✅ תסריט #{script_id} אושר ונשמר כדוגמה ללמידה")
        return ""

    if cmd.startswith("שפר "):
        script_id = int(cmd[4:].strip())
        feedback = input("מה לשפר? ").strip()
        result = improve_script(script_id, feedback)
        print(f"\n📝 תסריט משופר #{result['id']}:\n{result['script']}")
        return ""

    if cmd.startswith("למד "):
        parts = cmd[4:].strip().split("|")
        if len(parts) == 2:
            save_correction(parts[0].strip(), parts[1].strip(), parts[1].strip())
        return ""

    if cmd.startswith("כלל "):
        save_style_rule(cmd[4:].strip())
        return ""

    if cmd == "תסריטים":
        data = get_approved_scripts()
        scripts = data.get("scripts", [])
        if not scripts:
            print("אין תסריטים עדיין")
        for s in scripts:
            status = "✅" if s.get("status") == "approved" else "⏳"
            print(f"  {status} #{s['id']} [{s['date']}] {s['topic']}")
            print(f"     הוק: {s['hook'][:80]}")
        return ""

    if cmd == "פידבק":
        feedback = get_feedback()
        print("\n📚 מה שנלמד עד כה:")
        print("\n🔧 תיקונים:")
        for c in feedback.get("corrections", []):
            print(f"  ❌ {c['wrong']}")
            print(f"  ✅ {c['correct']}")
            print(f"  📌 כלל: {c['rule']}\n")
        print("\n📋 כללי סגנון:")
        for r in feedback.get("style_rules", []):
            print(f"  • {r}")
        return ""

    if cmd == "עזרה":
        print(COMMANDS)
        return ""

    if cmd in ["יציאה", "exit", "quit"]:
        print("\nשלום! 👋")
        sys.exit(0)

    return None


def chat_with_claude(user_input: str, history: list) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    history.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        max_tokens=1000,
        system=build_system_prompt(),
        messages=history
    )

    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})

    if any(phrase in user_input for phrase in ["לא נכון", "לא ככה", "טעית", "תקן", "שגוי"]):
        answer = input("\n💾 לשמור את זה כלמידה? (כן/לא) ").strip()
        if answer == "כן":
            correction = input("מה הכלל הנכון? ").strip()
            save_correction(user_input, reply, correction, context="שיחה")

    return reply


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ חסר ANTHROPIC_API_KEY ב-.env")
        sys.exit(1)
    if not os.getenv("APIFY_API_KEY"):
        print("❌ חסר APIFY_API_KEY ב-.env")
        sys.exit(1)

    print_banner()
    history = []

    while True:
        try:
            user_input = input("\nיוסי > ").strip()
            if not user_input:
                continue

            result = handle_command(user_input, history)
            if result is None:
                reply = chat_with_claude(user_input, history)
                print(f"\n🤖 {reply}")
        except KeyboardInterrupt:
            print("\n\nשלום! 👋")
            break
        except Exception as e:
            print(f"\n❌ שגיאה: {e}")


if __name__ == "__main__":
    main()
