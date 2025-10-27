from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = "secret"

DATA_FILE = os.path.join("static", "data.json")

# --- Helper functions ---
def load_reminders():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_reminders(reminders):
    # ensure static folder exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(reminders, f, indent=4)

# --- Routes ---
@app.route('/')
def home():
    reminders = load_reminders()
    return render_template("reminder.html", reminders=reminders)

@app.route('/add', methods=['POST'])
def add_reminder():
    medicine = request.form.get('medicine')
    time = request.form.get('time')
    date = request.form.get('date')

    if medicine and time and date:
        reminders = load_reminders()
        reminders.append({"medicine": medicine, "time": time, "date": date})
        save_reminders(reminders)
        flash("Reminder added successfully!", "success")
    else:
        flash("Please fill all fields!", "error")
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
    # Create static folder and data file if missing
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
    app.run(debug=True)
