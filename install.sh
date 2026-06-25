#!/bin/bash
# התקנת יוסי סושיאל אייג'נט

echo ""
echo "========================================"
echo "   מתקין את יוסי סושיאל אייג'נט..."
echo "========================================"
echo ""

# בדיקה שPython קיים
if ! command -v python3 &> /dev/null; then
    echo "❌ Python לא מותקן."
    echo "   הורד מ: https://www.python.org/downloads/"
    echo "   אחרי ההתקנה הרץ שוב את הסקריפט הזה."
    exit 1
fi

echo "✅ Python נמצא: $(python3 --version)"

# התקנת תלויות
echo ""
echo "📦 מתקין חבילות..."
pip3 install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ שגיאה בהתקנת חבילות. נסה להריץ:"
    echo "   pip3 install -r requirements.txt"
    exit 1
fi

echo "✅ חבילות הותקנו"

# יצירת קובץ .env אם לא קיים
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  נוצר קובץ .env — צריך למלא את המפתחות!"
else
    echo "✅ קובץ .env קיים"
fi

echo ""
echo "========================================"
echo "✅ ההתקנה הושלמה!"
echo ""
echo "לפני שמתחילים — תמלא 2 מפתחות בקובץ .env:"
echo "  ANTHROPIC_API_KEY=..."
echo ""
echo "להפעלה: python3 agent.py"
echo "========================================"
