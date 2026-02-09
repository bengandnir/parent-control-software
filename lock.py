# קובץ: site_blocker.py
import os

# הגדרות נתיבים
WINDOW_HOST = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "127.0.0.1"
SITES_FILE = "sites.txt"


def get_sites_list():
    """קורא את רשימת האתרים מהקובץ ומחזיר רשימה"""
    if not os.path.exists(SITES_FILE):
        return []
    try:
        with open(SITES_FILE, "r") as f:
            content = f.read()
            # מפרק לפי פסיקים ומנקה רווחים
            return [s.strip() for s in content.replace('\n', ',').split(',') if s.strip()]
    except:
        return []


def block_sites():
    sites = get_sites_list()
    if not sites:
        return "no_sites"

    try:
        with open(WINDOW_HOST, 'r+') as hostfile:
            content = hostfile.read()
            for site in sites:
                # חוסם את הדומיין הנקי
                if site not in content:
                    hostfile.write(REDIRECT_IP + ' ' + site + '\n')

                # חוסם גם את גרסת ה-www
                www_site = "www." + site
                if www_site not in content:
                    hostfile.write(REDIRECT_IP + ' ' + www_site + '\n')
        return "blocked"
    except PermissionError:
        return "admin_error"
    except Exception as e:
        return str(e)


def release_sites():

    sites = get_sites_list()
    try:
        with open(WINDOW_HOST, 'r+') as hostfile:
            lines = hostfile.readlines()
            hostfile.seek(0)
            for line in lines:

                if not any(site in line for site in sites):
                    hostfile.write(line)
            hostfile.truncate()
        return "released"
    except PermissionError:
        return "admin_error"
    except Exception as e:
        return str(e)


def add_site_to_list(new_site):

    try:
        with open(SITES_FILE, "a") as f:
            # אם הקובץ לא ריק, נוסיף פסיק לפני
            if os.path.getsize(SITES_FILE) > 0:
                f.write("," + new_site)
            else:
                f.write(new_site)
        return "added"
    except Exception as e:
        return str(e)