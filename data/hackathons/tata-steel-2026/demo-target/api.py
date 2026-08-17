import os, sqlite3
def get_user(uid):
    conn = sqlite3.connect("app.db")
    q = "SELECT * FROM users WHERE id = '%s'" % uid   # SQL injection
    return conn.execute(q).fetchall()
def ping(host):
    os.system("ping -c 1 " + host)                     # command injection
