#!/bin/bash
# validate_arabic.sh — التحقق السريع من ملف DOCX العربي

FILE="${1:-output.docx}"

if [ ! -f "$FILE" ]; then
  echo "❌ الملف غير موجود: $FILE"
  exit 1
fi

echo "🔍 جاري التحقق من: $FILE"
python3 /mnt/skills/public/docx/scripts/office/validate.py "$FILE"

if [ $? -eq 0 ]; then
  echo "✅ الملف صحيح وجاهز للتسليم"
else
  echo "❌ يوجد أخطاء — راجع المخرجات أعلاه"
fi
