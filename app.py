from flask import Flask, render_template, request, redirect, url_for, session
from database import get_db, init_db
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "changethislater"

with app.app_context():
    init_db()

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    habits = conn.execute("SELECT * FROM habits WHERE user_id = ?", (session["user_id"],)).fetchall()
    conn.close()
    return render_template("index.html", habits=habits)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        conn = get_db()
        existing_user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if existing_user:
            conn.close()
            return "An account with that email already exists"
        conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("home"))
        return "Invalid email or password"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/create", methods=["POST"])
def create():
    if "user_id" not in session:
        return redirect(url_for("login"))
    habit_name = request.form["habit_name"]
    conn = get_db()
    conn.execute("INSERT INTO habits (name, user_id) VALUES (?, ?)", (habit_name, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/complete/<int:habit_id>", methods=["POST"])
def complete(habit_id):
    conn = get_db()
    habit = conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
    if habit is None:
        conn.close()
        return redirect(url_for("home"))
    today = str(date.today())
    if habit["last_completed"] == today:
        conn.close()
        return redirect(url_for("home"))
    if habit["last_completed"] == str(date.fromordinal(date.today().toordinal() - 1)):
        new_streak = habit["streak"] + 1
    else:
        new_streak = 1
    conn.execute("UPDATE habits SET streak = ?, last_completed = ? WHERE id = ?", (new_streak, today, habit_id))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/delete/<int:habit_id>", methods=["POST"])
def delete(habit_id):
    conn = get_db()
    conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)