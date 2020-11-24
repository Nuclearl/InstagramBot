import sqlite3, datetime

def create_post(link, referal):
    conn = sqlite3.connect("db/data.db", timeout=10)
    c = conn.cursor()
    try:
        sql = "insert into posts (link, referal) values (?,?)"
        c.execute(sql, (link, referal))
    except sqlite3.DatabaseError as error:
        print("Error:", error)

    conn.commit()
    c.close()
    if conn:
        conn.close()

def store_liked_post(user_id, list_post):
    conn = sqlite3.connect("db/data.db", timeout=10)
    c = conn.cursor()
    try:
        for post in list_post:
            sql = "insert into liked_posts (user_id, post) values (?,?)"
            c.execute(sql, (user_id, post))
    except sqlite3.DatabaseError as error:
        print("Error:", error)

    conn.commit()
    c.close()
    if conn:
        conn.close()

def delete_liked_post(user_id, link):
    conn = sqlite3.connect("db/data.db", timeout=10)
    c = conn.cursor()
    try:
        sql = "DELETE FROM liked_posts WHERE user_id = ? and post= ?"
        c.execute(sql, (user_id, link))
    except sqlite3.DatabaseError as error:
        print("Error:", error)

    conn.commit()
    c.close()
    if conn:
        conn.close()

def delete_first_record():
    conn = sqlite3.connect("db/data.db", timeout=10)
    c = conn.cursor()
    try:
        result = c.execute("SELECT * FROM posts LIMIT 1").fetchone()
        c.execute("delete from posts where id = ?", (result[0], ))
    except sqlite3.DatabaseError as error:
        print("Error:", error)

    conn.commit()
    c.close()
    if conn:
        conn.close()


def change_last_visit(user_id):
    conn = sqlite3.connect("db/data.db", timeout=10)
    c = conn.cursor()
    list_users = c.execute("SELECT user_id FROM users").fetchall()
    list_users = [int(i[0]) for i in list_users]
    if user_id in list_users:
        now = datetime.datetime.now()
        c.execute("UPDATE users SET last_visit = ? WHERE user_id = ?", (now, user_id))
    else:
        now = datetime.datetime.now()
        c.execute("INSERT INTO users (user_id, last_visit) values (?,?)", (user_id, now))
    conn.commit()
    c.close()
    if conn:
        conn.close()

def get_last_visit(user_id):
    conn = sqlite3.connect("db/data.db", timeout=10)
    c = conn.cursor()
    try:
        result = c.execute("SELECT last_visit FROM users WHERE user_id =?", (user_id ,)).fetchone()[0]
    except:
        c.close()
        if conn:
            conn.close()
        return False
    c.close()
    if conn:
        conn.close()
    return result

def change_last_visit_username(user_id):
    conn = sqlite3.connect("db/data.db", timeout=10)
    c = conn.cursor()
    list_users = c.execute("SELECT username FROM instagram_username").fetchall()
    list_users = [i[0] for i in list_users]
    if user_id in list_users:
        now = datetime.datetime.now()
        c.execute("UPDATE instagram_username SET last_visit = ? WHERE username = ?", (now, user_id))
    else:
        now = datetime.datetime.now()
        c.execute("INSERT INTO instagram_username (username, last_visit) values (?,?)", (user_id, now))
    conn.commit()
    c.close()
    if conn:
        conn.close()

def get_last_visit_username(user_id):
    conn = sqlite3.connect("db/data.db", timeout=10)
    c = conn.cursor()
    try:
        result = c.execute("SELECT last_visit FROM instagram_username WHERE username =?", (user_id ,)).fetchone()[0]
    except:
        c.close()
        if conn:
            conn.close()
        return False
    c.close()
    if conn:
        conn.close()
    return result





