from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Temporary storage (no database yet)
users = {}
reminders_data = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    users[username] = password
    reminders_data[username] = []
    return redirect(url_for('reminder_page', username=username))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == password:
        return redirect(url_for('reminder_page', username=username))
    else:
        return "❌ Invalid username or password. Try again!"

@app.route('/reminder/<username>')
def reminder_page(username):
    reminders = reminders_data.get(username, [])
    return render_template('reminder.html', username=username, reminders=reminders)

@app.route('/add_reminder/<username>', methods=['POST'])
def add_reminder(username):
    name = request.form['name']
    time_input = request.form['time'].strip()

    # Validate 12-hour format with AM/PM
    try:
        valid_time = datetime.strptime(time_input, "%I:%M %p")
        formatted_time = valid_time.strftime("%I:%M %p")
    except ValueError:
        reminders = reminders_data.get(username, [])
        error_message = "❌ Invalid time format! Please enter like '1:25 PM'."
        return render_template('reminder.html', username=username, reminders=reminders, error_message=error_message)

    reminders_data[username].append({'name': name, 'time': formatted_time})
    return redirect(url_for('reminder_page', username=username))

@app.route('/logout', methods=['POST'])
def logout():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
