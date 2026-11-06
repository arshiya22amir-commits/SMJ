import os
import sqlite3
import urllib.request
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-before-deployment")
DB_PATH = os.path.join(os.path.dirname(__file__), "smj.db")
SERVER_ADDRESS = os.environ.get("SERVER_ADDRESS", "YOUR-SERVER-IP")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@smj.local")

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'در انتظار',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("برای ادامه ابتدا وارد حساب خود شوید.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            flash("دسترسی مدیریت برای این حساب فعال نیست.", "danger")
            return redirect(url_for("index"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    with db() as con:
        news = con.execute("SELECT * FROM news ORDER BY id DESC LIMIT 3").fetchall()
    return render_template("index.html", news=news, server_address=SERVER_ADDRESS)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 8 or "@" not in email:
            flash("نام کاربری باید حداقل ۳ حرف و رمز عبور حداقل ۸ کاراکتر باشد.", "warning")
            return render_template("register.html")
        try:
            with db() as con:
                con.execute(
                    "INSERT INTO users(username,email,password_hash) VALUES(?,?,?)",
                    (username, email, generate_password_hash(password))
                )
            flash("حساب شما ساخته شد؛ حالا وارد شوید.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("این نام کاربری یا ایمیل قبلاً ثبت شده است.", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with db() as con:
            user = con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = (email == ADMIN_EMAIL)
            flash("خوش آمدی!", "success")
            return redirect(url_for("admin") if session["is_admin"] else url_for("index"))
        flash("ایمیل یا رمز عبور اشتباه است.", "danger")
    return render_template("login.html")

@app.route("/team")
def team():
    # آواتارهای Steve و Alex فعلاً پیش‌فرض هستند؛ با دریافت آیدی Minecraft قابل شخصی‌سازی‌اند.
    team_members = [
        {"name": "جواد کریت", "role": "OWNER", "description": "Founder & Network Owner", "avatar": "https://mc-heads.net/avatar/Steve/128", "tone": "owner"},
        {"name": "ماهان کرشر", "role": "OWNER", "description": "Founder & Network Owner", "avatar": "https://mc-heads.net/avatar/Alex/128", "tone": "owner"},
        {"name": "مانی ثابتی", "role": "CO-OWNER", "description": "Network Co-Owner", "avatar": "https://mc-heads.net/avatar/Steve/128", "tone": "coowner"},
        {"name": "سارنگ گیمینگ", "role": "MANAGER", "description": "Team & Server Management", "avatar": "https://mc-heads.net/avatar/Alex/128", "tone": "manager"},
        {"name": "طاها پناهی", "role": "SR ADMIN", "description": "Senior Administration", "avatar": "https://mc-heads.net/avatar/Steve/128", "tone": "admin"},
        {"name": "عرشیا (سالوادور)", "role": "WEB DESIGNER & DEVELOPER", "description": "Website Design & Development", "avatar": "https://mc-heads.net/avatar/Alex/128", "tone": "developer"},
        {"name": "مهدی", "role": "BUILDER", "description": "World & Map Building", "avatar": "https://mc-heads.net/avatar/Steve/128", "tone": "builder"},
    ]
    return render_template("team.html", team_members=team_members)

@app.route("/shop")
def shop():
    # محصولات فعلاً نمایشی هستند؛ خرید و پرداخت واقعی بعداً به درگاه متصل می‌شود.
    ranks = [
        {"name": "VIP", "price": "قیمت به‌زودی", "features": ["نشان اختصاصی", "امکانات ویژه داخل بازی", "پشتیبانی اولویت‌دار"], "style": "rank-vip"},
        {"name": "MVP", "price": "قیمت به‌زودی", "features": ["تمام امکانات VIP", "امتیازها و قابلیت‌های بیشتر", "نشان ویژه‌تر"], "style": "rank-mvp"},
        {"name": "LEGEND", "price": "قیمت به‌زودی", "features": ["تمام امکانات رنک‌های قبلی", "ظاهر اختصاصی", "امکانات ویژه بیشتر"], "style": "rank-legend"}
    ]
    return render_template("shop.html", ranks=ranks)

@app.route("/profile")
@login_required
def profile():
    with db() as con:
        user = con.execute("SELECT username,email,created_at FROM users WHERE id=?", (session["user_id"],)).fetchone()
        tickets = con.execute("SELECT * FROM support_tickets WHERE user_id=? ORDER BY id DESC", (session["user_id"],)).fetchall()
    return render_template("profile.html", user=user, tickets=tickets)

@app.route("/support", methods=["GET", "POST"])
@login_required
def support():
    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()
        if len(subject) < 3 or len(message) < 10:
            flash("عنوان حداقل ۳ حرف و پیام حداقل ۱۰ حرف باشد.", "warning")
        else:
            with db() as con:
                con.execute("INSERT INTO support_tickets(user_id,subject,message) VALUES(?,?,?)",
                            (session["user_id"], subject, message))
            flash("درخواست پشتیبانی ثبت شد.", "success")
            return redirect(url_for("profile"))
    return render_template("support.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("از حساب خارج شدی.", "success")
    return redirect(url_for("index"))

@app.route("/admin", methods=["GET", "POST"])
@login_required
@admin_required
def admin():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        if title and body:
            with db() as con:
                con.execute("INSERT INTO news(title,body) VALUES(?,?)", (title, body))
            flash("خبر جدید منتشر شد.", "success")
            return redirect(url_for("admin"))
        flash("عنوان و متن خبر را وارد کن.", "warning")
    with db() as con:
        news = con.execute("SELECT * FROM news ORDER BY id DESC").fetchall()
        users_count = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    return render_template("admin.html", news=news, users_count=users_count)

@app.post("/admin/news/<int:news_id>/delete")
@login_required
@admin_required
def delete_news(news_id):
    with db() as con:
        con.execute("DELETE FROM news WHERE id=?", (news_id,))
    flash("خبر حذف شد.", "success")
    return redirect(url_for("admin"))

@app.get("/api/status")
def server_status():
    if not SERVER_ADDRESS or SERVER_ADDRESS == "YOUR-SERVER-IP":
        return jsonify({"configured": False, "online": False, "message": "آدرس سرور هنوز تنظیم نشده است."})
    try:
        url = "https://api.mcsrvstat.us/3/" + SERVER_ADDRESS
        req = urllib.request.Request(url, headers={"User-Agent": "SMJ-Network-Website/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
        return jsonify({
            "configured": True,
            "online": bool(data.get("online")),
            "players": data.get("players", {}).get("online", 0),
            "max": data.get("players", {}).get("max", 0),
            "version": data.get("version", "نامشخص")
        })
    except Exception:
        return jsonify({"configured": True, "online": False, "message": "وضعیت سرور فعلاً قابل دریافت نیست."})

if __name__ == "__main__":
    init_db()
    app.run(debug=False)
