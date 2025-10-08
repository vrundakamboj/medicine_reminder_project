from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secretkey'

DATA_FILE = 'data.json'

# Load reminders
def load_reminders():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

# Save reminders
def save_reminders(reminders):
    with open(DATA_FILE, 'w') as f:
        json.dump(reminders, f, indent=4)

@app.route('/')
def index():
    reminders = load_reminders()
    return render_template('reminder.html', reminders=reminders)

@app.route('/add', methods=['POST'])
def add_reminder():
    medicine = request.form['medicine'].strip()
    time = request.form['time'].strip()
    date = request.form['date'].strip()

    if not medicine or not time or not date:
        flash("All fields are required!", "error")
        return redirect(url_for('index'))

    try:
        datetime.strptime(time, "%H:%M")
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        flash("Invalid time or date format!", "error")
        return redirect(url_for('index'))

    reminders = load_reminders()
    reminders.append({"medicine": medicine, "time": time, "date": date})
    save_reminders(reminders)

    flash("Reminder added successfully!", "success")
    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete_reminder(index):
    reminders = load_reminders()
    if 0 <= index < len(reminders):
        removed = reminders.pop(index)
        save_reminders(reminders)
        flash(f"Deleted reminder for {removed['medicine']}", "success")
    else:
        flash("Invalid reminder index!", "error")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
