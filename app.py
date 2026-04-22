from flask import Flask, render_template, request, redirect, url_for
from database import get_db, init_db
from datetime import date

app = Flask(__name__)

with app.app_context():
    init_db()

@app.route("/")
def home():
    conn = get_db()
    habits = conn.execute("SELECT * FROM habits").fetchall()
    conn.close()
    return render_template("index.html", habits=habits)

@app.route("/create", methods=["POST"])
def create():
    habit_name = request.form["habit_name"]
    conn = get_db()
    conn.execute("INSERT INTO habits (name) VALUES (?)", (habit_name,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.route("/complete/<int:habit_id>", methods=["POST"])
def complete(habit_id):
    conn = get_db()
    habit = conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
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