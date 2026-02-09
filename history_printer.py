import os
import sqlite3
import shutil
import json


def get_chrome_history():
    """
    שולף את היסטוריית הגלישה של כרום בצורה ידנית.
    עוקף נעילת קבצים על ידי יצירת עותק זמני.
    """

    # 1. איתור נתיב ההיסטוריה של כרום (Windows)
    app_data = os.getenv('LOCALAPPDATA')
    if not app_data:
        return json.dumps({"Error": "Could not find LocalAppData"})

    history_db = os.path.join(app_data, r'Google\Chrome\User Data\Default\History')

    # שם לקובץ הזמני
    temp_history_db = 'temp_history_db_copy'

    # בדיקה אם הקובץ קיים
    if not os.path.exists(history_db):
        return json.dumps({"Error": "Chrome history file not found"})

    try:
        # 2. העתקת הקובץ (החלק הקריטי!)
        # מעתיקים לקובץ זמני כדי לעקוף את הנעילה של הדפדפן
        shutil.copy2(history_db, temp_history_db)

        # 3. התחברות למסד הנתונים (SQL)
        conn = sqlite3.connect(temp_history_db)
        cursor = conn.cursor()

        # שאילתה: שליפת ה-URL ומספר הביקורים, ממוין מהגדול לקטן, 30 התוצאות הראשונות
        query = "SELECT url, visit_count FROM urls ORDER BY visit_count DESC LIMIT 30"
        cursor.execute(query)
        results = cursor.fetchall()

        conn.close()  # סגירת חיבור

        # 4. עיבוד הנתונים למילון (כדי שהלקוח יוכל להציג יפה)
        sites_count = {}

        for row in results:
            url = row[0]
            count = row[1]

            # ניקוי ה-URL כדי להשאיר רק את הדומיין (למשל google.com)
            try:
                # לוקח את החלק אחרי // ולפני ה / הראשון
                domain = url.split('//')[-1].split('/')[0]

                # מוריד www. אם קיים
                if domain.startswith('www.'):
                    domain = domain[4:]

                # סינון זבל (שורות ריקות וכו')
                if not domain: continue

                # סכימה (אם הדומיין כבר קיים, נוסיף לו את הביקורים)
                sites_count[domain] = sites_count.get(domain, 0) + count

            except:
                pass  # אם הכתובת מוזרה, מדלגים

        # מיון המילון הסופי
        sorted_sites = dict(sorted(sites_count.items(), key=lambda item: item[1], reverse=True))

        # המרה ל-JSON (מחרוזת)
        return json.dumps(sorted_sites)

    except Exception as e:
        return json.dumps({"Error": str(e)})

    finally:
        # 5. ניקיון - מחיקת הקובץ הזמני תמיד (גם אם הייתה שגיאה)
        if os.path.exists(temp_history_db):
            try:
                os.remove(temp_history_db)
            except:
                pass