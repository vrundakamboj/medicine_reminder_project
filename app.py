from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import threading
import time

app = Flask(__name__)
app.secret_key = "secret"

# Temporary in-memory storage (for now)
reminders = []

@app.route('/')
def index():
    return render_template('index.html', reminders=reminders)

@app.route('/add', methods=['GET', 'POST'])
def add_reminder():
    if request.method == 'POST':
        name = request.form['name']
        time_str = request.form['time']
        if name and time_str:
            reminders.append({'name': name, 'time': time_str})
            flash('Reminder added successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please fill all fields!', 'error')
    return render_template('add_reminder.html')

@app.route('/delete/<int:index>')
def delete_reminder(index):
    try:
        reminders.pop(index)
        flash('Reminder deleted successfully!', 'success')
    except IndexError:
        flash('Reminder not found!', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
