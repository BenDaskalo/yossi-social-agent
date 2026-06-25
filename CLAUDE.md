# יוסי סושיאל אייג'נט — הוראות לקלוד קוד

## כשיוסי כותב "התקן" או "הגדר" או "setup"

בצע את הצעדים הבאים **בסדר הזה**, בלי לשאול שאלות מיותרות:

### צעד 1 — בדוק Python
```bash
python3 --version
```
אם Python לא קיים — הגד ליוסי:
"Python לא מותקן. הורד מ: https://www.python.org/downloads/ ואחרי ההתקנה כתוב שוב 'התקן'"
ועצור.

### צעד 2 — התקן חבילות
```bash
pip3 install -r requirements.txt
```

### צעד 3 — בדוק אם .env קיים
אם `.env` לא קיים — צור אותו מ-`.env.example`:
```bash
cp .env.example .env
```

### צעד 4 — בדוק אם ANTHROPIC_API_KEY מוגדר
פתח את `.env` ובדוק אם השורה `ANTHROPIC_API_KEY=` עדיין מכילה `your_anthropic_api_key_here`.

אם כן — שאל את יוסי:
"יוסי, תכניס את מפתח ה-Anthropic שלך (מתחיל ב-sk-ant-):"

כשיוסי שולח את המפתח — הכנס אותו לקובץ `.env` בשורה `ANTHROPIC_API_KEY=`.

### צעד 5 — הרץ את הסוכן
```bash
python3 agent.py
```

---

## כשיוסי כותב "הפעל" או "התחל" או "run"

אם `.env` קיים ו-`ANTHROPIC_API_KEY` מוגדר:
```bash
python3 agent.py
```

אם לא — בצע "התקן" קודם.

---

## כשיוסי כותב "עדכן"

משוך עדכונים ממקור הפרויקט:
```bash
curl -L https://github.com/BenDaskalo/yossi-social-agent/archive/refs/heads/main.zip -o update.zip
unzip -o update.zip "yossi-social-agent-main/agent.py" "yossi-social-agent-main/memory_manager.py" "yossi-social-agent-main/scraper.py" "yossi-social-agent-main/script_writer.py" "yossi-social-agent-main/requirements.txt" -d /tmp/
cp /tmp/yossi-social-agent-main/*.py .
rm -rf update.zip /tmp/yossi-social-agent-main
pip3 install -r requirements.txt --quiet
```
הגד ליוסי: "✅ הסוכן עודכן. כתוב 'הפעל' כדי להמשיך."

---

## כשיוסי כותב "מפתח חדש" או "שנה מפתח"

שאל: "מה המפתח החדש?"
כשהוא שולח — עדכן את `.env`:
```python
# update ANTHROPIC_API_KEY in .env
```

---

## חוקי ברזל

- **אף פעם לא** להציג את ה-API key בטקסט גלוי בשיחה
- **תמיד** לאשר בסוף כל פעולה שהיא הצליחה לפני המעבר לצעד הבא
- **אם משהו נכשל** — הסבר בעברית פשוטה מה קרה ומה לעשות
- **שפה** — תמיד עברית עם יוסי

---

## מבנה הפרויקט

```
yossi-social-agent/
├── agent.py              ← הסוכן הראשי (מריצים אותו)
├── memory_manager.py     ← ניהול זיכרון ולמידה
├── scraper.py            ← סריקת אינסטגרם
├── script_writer.py      ← כתיבת תסריטים
├── memory/               ← כל הזיכרון (לא למחוק!)
│   ├── profile.json
│   ├── feedback.json
│   ├── approved_scripts.json
│   └── competitor_insights.json
├── .env                  ← מפתחות API (לא לשתף!)
└── requirements.txt
```
