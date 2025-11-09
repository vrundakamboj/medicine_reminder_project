# Final code.py — Light themed Medication Reminder with Login/Signup
# Minimal changes: adds topmost alarm pop-up; preserves existing voice behavior (Windows pyttsx3 / macOS say)
import tkinter as tk
from tkinter import ttk, messagebox
import csv, os, datetime
import dateutil.parser
from pathlib import Path
import platform

# ---------- Config ----------
USERS_FILE = "users.csv"
MEDS_FILE_TEMPLATE = "meds_{}.csv"   # per-user medication file
REMINDER_CHECK_MS = 30_000           # 30 seconds automatic check

# ---------- Voice / Sound (preserve original behavior) ----------
_system = platform.system()
if _system == "Windows":
    # use pyttsx3 on Windows for stable offline TTS (no beeps)
    try:
        import pyttsx3
    except Exception:
        pyttsx3 = None

def speak_and_ding(text):
    """
    Preserve the voice behavior:
    - On Windows: use pyttsx3 if available (no beep)
    - On macOS: use `say`
    - Else: fallback to printing
    """
    try:
        if _system == "Windows":
            if pyttsx3 is not None:
                try:
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
                except Exception:
                    # fallback to PowerShell TTS if pyttsx3 fails
                    try:
                        safe_text = text.replace('"', '`"')
                        ps_command = f'Add-Type –AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{safe_text}");'
                        os.system(f'powershell -Command "{ps_command}"')
                    except Exception:
                        print(text)
            else:
                # if pyttsx3 not installed, try PowerShell method
                try:
                    safe_text = text.replace('"', '`"')
                    ps_command = f'Add-Type –AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{safe_text}");'
                    os.system(f'powershell -Command "{ps_command}"')
                except Exception:
                    print(text)
        elif _system == "Darwin":  # macOS
            try:
                os.system(f'say "{text}" &')
            except Exception:
                print(text)
        else:
            print(text)
    except Exception:
        # ultimate fallback
        print(text)

def show_alarm_popup(parent, message):
    """
    Topmost alarm-style pop-up that shows the reminder and has a Dismiss button.
    Keeps focus on top.
    """
    try:
        popup = tk.Toplevel(parent)
        popup.title("⏰ Medication Reminder")
        popup.geometry("420x160")
        popup.configure(bg="#FFEBEE")
        popup.attributes("-topmost", True)
        popup.resizable(False, False)

        tk.Label(popup, text="Time to take your medication!", font=("Helvetica", 16, "bold"),
                 bg="#FFEBEE", fg="#C62828").pack(pady=(18,8))
        tk.Label(popup, text=message, font=("Helvetica", 13), bg="#FFEBEE").pack(pady=(0,10))

        def dismiss():
            try:
                popup.destroy()
            except Exception:
                pass

        ttk.Button(popup, text="Dismiss", command=dismiss).pack(pady=(6,12))

        # bring to front and focus
        try:
            popup.lift()
            popup.focus_force()
        except Exception:
            pass

    except Exception:
        # fallback to simple messagebox if Toplevel fails
        try:
            messagebox.showinfo("Medication Reminder", message)
        except Exception:
            print("Reminder:", message)

def show_notification_title_message(title, message, parent=None):
    """
    Cross-platform small notification: on macOS we use osascript (if available),
    on Windows we show a tkinter messagebox (or popup).
    This wrapper is not changing voice logic — it's just for small notifications.
    """
    if _system == "Darwin":
        try:
            os.system(f'''osascript -e 'display notification "{message}" with title "{title}"' ''')
        except Exception:
            try:
                messagebox.showinfo(title, message)
            except Exception:
                print(title, message)
    else:
        # Use our topmost popup for alarm feel (parent window passed when available)
        if parent is not None:
            show_alarm_popup(parent, message)
        else:
            try:
                # simple messagebox fallback
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo(title, message)
                root.destroy()
            except Exception:
                print(title, message)

# ---------- Helpers ----------
def ensure_users_file():
    if not Path(USERS_FILE).exists():
        with open(USERS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password"])

def user_meds_file(username):
    return MEDS_FILE_TEMPLATE.format(username)

def ensure_user_meds(username):
    fn = user_meds_file(username)
    if not Path(fn).exists():
        with open(fn, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Medication","Dosage","Frequency","Time"])  # header

def read_users():
    ensure_users_file()
    with open(USERS_FILE, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        return [row for row in reader if row]

def add_user(username, password):
    ensure_users_file()
    with open(USERS_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([username, password])

def validate_login(username, password):
    users = read_users()
    for u,p in users:
        if u == username and p == password:
            return True
    return False

# ---------- GUI: Login / Signup ----------
def open_signup(window):
    top = tk.Toplevel(window)
    top.title("Sign Up")
    top.geometry("380x300")
    top.configure(bg="#F7FBF9")
    top.resizable(False, False)

    ttk.Label(top, text="Create an account", font=("Helvetica", 16, "bold")).pack(pady=(18,8))

    frm = ttk.Frame(top, padding=12)
    frm.pack()

    ttk.Label(frm, text="Username:").grid(row=0, column=0, sticky="w", pady=6)
    ent_user = ttk.Entry(frm, width=28)
    ent_user.grid(row=0, column=1, pady=6)

    ttk.Label(frm, text="Password:").grid(row=1, column=0, sticky="w", pady=6)
    ent_pass = ttk.Entry(frm, width=28, show="*")
    ent_pass.grid(row=1, column=1, pady=6)

    def do_signup():
        user = ent_user.get().strip()
        pwd  = ent_pass.get().strip()
        if not user or not pwd:
            messagebox.showwarning("Missing", "Please enter username and password.")
            return
        users = read_users()
        if any(u==user for u,_ in users):
            messagebox.showerror("Exists", "Username already exists.")
            return
        add_user(user, pwd)
        ensure_user_meds(user)
        messagebox.showinfo("Success", "Account created! You can now login.")
        top.destroy()

    btn = ttk.Button(top, text="Create Account", command=do_signup)
    btn.pack(pady=14)
    speak_and_ding("Sign up opened. Please enter username and password.")

def open_login(window, on_success):
    window.title("Medication Reminder — Login")
    window.geometry("560x420")
    window.configure(bg="#F7FBF9")
    window.resizable(False, False)

    # Clear any existing widgets
    for w in window.winfo_children():
        w.destroy()

    # Title
    lbl_title = tk.Label(window, text="Welcome to HealthMate", font=("Helvetica", 26, "bold"), bg="#F7FBF9", fg="#2E7D32")
    lbl_title.pack(pady=(28,6))

    lbl_sub = tk.Label(window, text="Login to manage your medication reminders", font=("Helvetica", 12), bg="#F7FBF9")
    lbl_sub.pack(pady=(0,18))

    frm = ttk.Frame(window, padding=12)
    frm.pack()

    ttk.Label(frm, text="Username:", width=14).grid(row=0, column=0, sticky="w", pady=8)
    ent_user = ttk.Entry(frm, width=36)
    ent_user.grid(row=0, column=1, pady=8)

    ttk.Label(frm, text="Password:", width=14).grid(row=1, column=0, sticky="w", pady=8)
    ent_pass = ttk.Entry(frm, width=36, show="*")
    ent_pass.grid(row=1, column=1, pady=8)

    def do_login():
        user = ent_user.get().strip()
        pwd  = ent_pass.get().strip()
        if validate_login(user, pwd):
            speak_and_ding("Login successful. Opening your dashboard.")
            on_success(window, user)   # <-- pass both window and username
        else:
            messagebox.showerror("Login failed", "Invalid username or password.")
            speak_and_ding("Login failed. Please try again.")

    btn_frame = ttk.Frame(window)
    btn_frame.pack(pady=18)

    ttk.Button(btn_frame, text="Login", command=do_login, width=16).grid(row=0, column=0, padx=8)
    ttk.Button(btn_frame, text="Sign Up", command=lambda: open_signup(window), width=16).grid(row=0, column=1, padx=8)

    # Small footer
    ttk.Label(window, text="Light theme • Auto-speak reminders • Local CSV storage", font=("Helvetica", 9), foreground="#5f6f66", background="#F7FBF9").pack(side="bottom", pady=12)

# ---------- Main App (per-user) ----------
def open_main_app(window, username):
    ensure_user_meds(username)
    meds_file = user_meds_file(username)

    # clear window
    for w in window.winfo_children():
        w.destroy()

    window.title(f"HealthMate — {username}")
    window.geometry("820x600")
    window.configure(bg="#F7FBF9")
    window.resizable(False, False)

    # center the window (cross-platform safe method)
    window.update_idletasks()
    w = window.winfo_width()
    h = window.winfo_height()
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    window.geometry(f'+{x}+{y}')

    # Header
    header = tk.Frame(window, bg="#F7FBF9")
    header.pack(pady=(18,8))
    tk.Label(header, text=f"Hello, {username}", font=("Helvetica", 22, "bold"), bg="#F7FBF9", fg="#2E7D32").pack()
    tk.Label(header, text="Your medication dashboard", font=("Helvetica", 12), bg="#F7FBF9").pack()

    # Center frame with add/view
    center = tk.Frame(window, bg="#F7FBF9")
    center.pack(pady=12, fill="both", expand=False)

    left = tk.Frame(center, bg="#F7FBF9", bd=0)
    left.grid(row=0, column=0, padx=(30,20), sticky="n")

    right = tk.Frame(center, bg="#F7FBF9")
    right.grid(row=0, column=1, padx=(20,30), sticky="n")

    # Add medication card (left)
    card1 = tk.Frame(left, bg="white", bd=0, relief="raised", padx=18, pady=14)
    card1.pack()
    tk.Label(card1, text="Add Medication", font=("Helvetica", 14, "bold"), bg="white").pack(anchor="w")
    tk.Label(card1, text="Enter details below to schedule a reminder", font=("Helvetica", 10), bg="white", fg="#5f6f66").pack(anchor="w", pady=(2,8))

    ttk.Label(card1, text="Medication name").pack(anchor="w", pady=(6,0))
    ent_name = ttk.Entry(card1, width=36)
    ent_name.pack(pady=4)

    ttk.Label(card1, text="Dosage (e.g., 500 mg)").pack(anchor="w", pady=(6,0))
    ent_dose = ttk.Entry(card1, width=36)
    ent_dose.pack(pady=4)

    ttk.Label(card1, text="Frequency (e.g., Once daily)").pack(anchor="w", pady=(6,0))
    ent_freq = ttk.Entry(card1, width=36)
    ent_freq.pack(pady=4)

    ttk.Label(card1, text="Time (24h HH:MM)").pack(anchor="w", pady=(6,0))
    ent_time = ttk.Entry(card1, width=36)
    ent_time.pack(pady=4)

    def save_medicine():
        name = ent_name.get().strip()
        dose = ent_dose.get().strip()
        freq = ent_freq.get().strip()
        tstr = ent_time.get().strip()
        if not name or not tstr:
            messagebox.showwarning("Missing", "Please enter at least medication name and time.")
            return
        try:
            parsed = dateutil.parser.parse(tstr).strftime("%H:%M")
        except Exception:
            messagebox.showerror("Time error", "Time must be like 14:30 or 9:00 AM/PM.")
            return
        with open(meds_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name, dose, freq, parsed])
        messagebox.showinfo("Saved", f"{name} saved for {parsed}.")
        speak_and_ding(f"Saved medication {name} at {parsed}")
        ent_name.delete(0, tk.END)
        ent_dose.delete(0, tk.END)
        ent_freq.delete(0, tk.END)
        ent_time.delete(0, tk.END)
        refresh_list()

    ttk.Button(card1, text="Save Medication", command=save_medicine).pack(pady=(10,4))

    # View medications (right)
    card2 = tk.Frame(right, bg="white", bd=0, relief="raised", padx=12, pady=12)
    card2.pack()
    tk.Label(card2, text="Scheduled Medications", font=("Helvetica", 14, "bold"), bg="white").pack(anchor="w")
    tk.Label(card2, text="Tap a row to remove", font=("Helvetica", 10), bg="white", fg="#5f6f66").pack(anchor="w", pady=(2,8))

    listbox = tk.Listbox(card2, width=58, height=14, bd=0, font=("Helvetica", 12))
    listbox.pack(pady=(6,4))

    def refresh_list():
        listbox.delete(0, tk.END)
        if not Path(meds_file).exists():
            return
        with open(meds_file, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if not row: continue
                listbox.insert(tk.END, f"{row[0]}  |  {row[1]}  |  {row[2]}  |  {row[3]}")

    def remove_selected():
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("Select", "Choose a row to remove.")
            return
        i = sel[0]
        rows = []
        with open(meds_file, newline="") as f:
            reader = csv.reader(f)
            hdr = next(reader, None)
            for r in reader:
                rows.append(r)
        rows.pop(i)
        with open(meds_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(hdr if hdr else ["Medication","Dosage","Frequency","Time"])
            for r in rows:
                writer.writerow(r)
        refresh_list()
        speak_and_ding("Medication removed.")

    ttk.Button(card2, text="Remove Selected", command=remove_selected).pack(pady=(6,4))
    ttk.Button(card2, text="Refresh", command=refresh_list).pack(pady=(2,8))

    # Bottom controls
    bottom = tk.Frame(window, bg="#F7FBF9")
    bottom.pack(pady=18)

    def check_reminders_once(show_popup=True):
        now = datetime.datetime.now().strftime("%H:%M")
        if not Path(meds_file).exists():
            return
        triggered = []
        with open(meds_file, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)
            for r in reader:
                if not r: continue
                try:
                    name, dose, freq, tstr = r
                except ValueError:
                    continue
                try:
                    sched = dateutil.parser.parse(tstr).strftime("%H:%M")
                except Exception:
                    continue
                if sched == now:
                    triggered.append(name)
        if triggered:
            msg = " & ".join(triggered)
            # **POP-UP ALARM (topmost)** — minimal change, preserves voice function exactly
            if show_popup:
                show_alarm_popup(window, f"It's time to take: {msg}")
            # original voice call — unchanged
            speak_and_ding(f"It's time to take {msg}")

    def start_auto_check():
        check_reminders_once(show_popup=True)
        window.after(REMINDER_CHECK_MS, start_auto_check)

    ttk.Button(bottom, text="Check Reminders Now", command=lambda: check_reminders_once(True)).grid(row=0, column=0, padx=10)
    ttk.Button(bottom, text="Logout", command=lambda: (open_login(window, open_main_app), speak_and_ding("Logged out."))).grid(row=0, column=1, padx=10)

    refresh_list()
    window.after(5_000, start_auto_check)  # start after 5s

# ---------- App Start ----------
def main():
    ensure_users_file()
    root = tk.Tk()
    root.configure(bg="#F7FBF9")
    # starting size and center
    root.geometry("560x420")
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    root.geometry(f'+{x}+{y}')
    open_login(root, open_main_app)
    root.mainloop()

if __name__ == "__main__":
    main()
