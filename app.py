from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = "secret"

DATA_FILE = "static/data.json"

# Load reminders from JSON
def load_reminders():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# Save reminders to JSON
def save_reminders(reminders):
    with open(DATA_FILE, "w") as f:
        json.dump(reminders, f, indent=4)

@app.route('/')
def home():
    reminders = load_reminders()
    return render_template("reminder.html", reminders=reminders)

@app.route('/add', methods=['POST'])
def add_reminder():
    medicine = request.form['medicine']
    time = request.form['time']
    date = request.form['date']

    reminders = load_reminders()
    reminders.append({"medicine": medicine, "time": time, "date": date})
    save_reminders(reminders)

    flash("Reminder added successfully!", "success")
    return redirect(url_for("home"))

@app.route('/delete/<int:index>')
def delete_reminder(index):
    reminders = load_reminders()
    if 0 <= index < len(reminders):
        reminders.pop(index)
        save_reminders(reminders)
        flash("Reminder deleted successfully!", "success")
    else:
        flash("Reminder not found!", "error")
    return redirect(url_for("home"))

if __name__ == '__main__':
    # Ensure data file exists
    if not os.path.exists("static"):
        os.mkdir("static")
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
    app.run(debug=True)
