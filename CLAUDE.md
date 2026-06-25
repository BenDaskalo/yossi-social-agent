# יוסי סושיאל אייג'נט — הוראות לקלוד קוד

## פרומט ההתקנה הראשונית

כשיוסי מדביק את פרומט ההתקנה, בצע **בדיוק** את הצעדים הבאים:

### צעד 1 — מצא את הZIP בהורדות
```bash
find ~/Downloads -name "yossi-social-agent*.zip" | head -1
```
אם לא נמצא — אמור ליוסי: "לא מצאתי את הקובץ בתיקיית ההורדות. ודא שהורדת אותו ונסה שוב."

### צעד 2 — חלץ לתיקיית הבית
```bash
unzip -o ~/Downloads/yossi-social-agent-main.zip -d ~/
mv ~/yossi-social-agent-main ~/yossi-agent 2>/dev/null || true
```

### צעד 3 — בדוק Python
```bash
python3 --version
```
אם לא קיים — אמור: "Python לא מותקן. הורד מ: https://www.python.org/downloads/ ואחרי ההתקנה שלח 'מוכן'"

### צעד 4 — התקן חבילות
```bash
cd ~/yossi-agent && pip3 install -r requirements.txt --quiet
```

### צעד 5 — הכן .env
```bash
cp ~/yossi-agent/.env.example ~/yossi-agent/.env
```

### צעד 6 — שאל מפתח Anthropic
אמור ליוסי בדיוק:
"הכל מוכן ✅
עכשיו צריך מפתח Anthropic אחד.
כנס ל: https://console.anthropic.com/ → הירשם בחינם → API Keys → Create Key
העתק את המפתח ושלח אותו כאן."

כשיוסי שולח את המפתח — הכנס אותו לקובץ:
```bash
sed -i '' 's|ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=המפתח_שהוא_שלח|' ~/yossi-agent/.env
```

### צעד 7 — הרץ
```bash
cd ~/yossi-agent && python3 agent.py
```

---

## פרומט הפעלה רגילה (לפעמות הבאות)

```bash
cd ~/yossi-agent && python3 agent.py
```

---

## פרומט עדכון

```bash
curl -L https://github.com/BenDaskalo/yossi-social-agent/archive/refs/heads/main.zip -o ~/Downloads/update.zip
unzip -o ~/Downloads/update.zip "yossi-social-agent-main/agent.py" "yossi-social-agent-main/memory_manager.py" "yossi-social-agent-main/scraper.py" "yossi-social-agent-main/script_writer.py" -d /tmp/
cp /tmp/yossi-social-agent-main/*.py ~/yossi-agent/
rm -rf ~/Downloads/update.zip /tmp/yossi-social-agent-main
```

---

## חוקי ברזל

- לא להציג API key בטקסט גלוי
- תמיד עברית עם יוסי
- לאשר כל צעד לפני הבא
- אם משהו נכשל — להסביר פשוט ומה לעשות
