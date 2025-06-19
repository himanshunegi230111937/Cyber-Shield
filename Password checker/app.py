import os
import json
import re
import string
import time
import itertools
import hashlib
from flask_limiter import Limiter
from flask_mail import Mail, Message
import random
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecret"

limiter = Limiter(app)

def check_hash(word, input_val, hash_type):
    if hash_type == "md5":
        return hashlib.md5(word.encode()).hexdigest() == input_val
    elif hash_type == "sha1":
        return hashlib.sha1(word.encode()).hexdigest() == input_val
    elif hash_type == "sha256":
        return hashlib.sha256(word.encode()).hexdigest() == input_val
    return False




app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'CyberShieldTech1@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') # Use the 16-character app password here $env:MAIL_PASSWORD="yuinbiiclafsxoeb"
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
mail = Mail(app)

# Load users
try:
    with open('users.json', 'r') as f:
        users = json.load(f)
except:
    users = {}

def save_users():
    with open('users.json', 'w') as f:
        json.dump(users, f)

def get_profile_pic(username):
    user = users.get(username)
    if isinstance(user, dict):
        return user.get("profile_pic")
    return None

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        # Check if user/email already exists
        if username in users or any(u.get("email") == email for u in users.values() if isinstance(u, dict)):
            flash("Username or email already exists. Please login or use a different one.", "error")
            return render_template("register.html")
        otp = str(random.randint(100000, 999999))
        session["pending_user"] = {
            "username": username,
            "email": email,
            "phone": phone,
            "password": generate_password_hash(password),
            "otp": otp
        }
        msg = Message("Your OTP Code", sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Your OTP code is: {otp}"
        mail.send(msg)
        return redirect(url_for("verify_otp"))
    return render_template("register.html")

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "pending_user" not in session:
        return redirect(url_for("register"))
    if request.method == "POST":
        user_otp = request.form["otp"]
        if user_otp == session["pending_user"]["otp"]:
            username = session["pending_user"]["username"]
            users[username] = {
                "email": session["pending_user"]["email"],
                "phone": session["pending_user"]["phone"],
                "password": session["pending_user"]["password"],
                "profile_pic": None
            }
            save_users()
            session.pop("pending_user")
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Invalid OTP. Please try again.", "error")
    return render_template("verify_otp.html")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_input = request.form["username"]
        password = request.form["password"]
        user_key = None
        # Username or email login
        if login_input in users:
            user_key = login_input
        else:
            for uname, user_data in users.items():
                if isinstance(user_data, dict) and user_data.get("email") == login_input:
                    user_key = uname
                    break
        if user_key:
            user_data = users[user_key]
            pw_hash = user_data.get("password") if isinstance(user_data, dict) else user_data
            if check_password_hash(pw_hash, password):
                session["user"] = user_key
                return redirect(url_for("home"))
            else:
                flash("Incorrect Password", "error")
        else:
            flash("User not found. Please register.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    username = session["user"]
    profile_pic = get_profile_pic(username)
    user_data = users.get(username, {})
    # Example: collect previous data (could be extended)
    previous_data = user_data.get("history", [])
    return render_template("dashboard.html", profile_pic=profile_pic, previous_data=previous_data, username=username)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect(url_for("login"))
    username = session["user"]
    user = users.get(username)
    if request.method == "POST":
        user["email"] = request.form.get("email")
        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                user["profile_pic"] = filename
        save_users()
        flash("Profile updated!", "success")
        return redirect(url_for("profile"))
    return render_template("profile.html", user=user, username=username, profile_pic=user.get("profile_pic"))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/password_strength")
def password_strength():
    return render_template("password_strength.html")

@app.route("/password_cracker", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def password_cracker():
    if request.method == "GET":
        return render_template("password_cracker.html")
    hash_type = request.form.get("hashType", "md5")
    input_val = request.form.get("input")
    is_hash = request.form.get("isHash") == "true"
    attack_type = request.form.get("attackType", "dictionary")
    file = request.files.get("dictionary")
    attempts = 0
    found = False
    password = ""
    import time, string, itertools
    start = time.time()
    if not input_val:
        return jsonify({"error": "No input provided"}), 400
    if attack_type == "dictionary":
     if file and file.filename:
        file.seek(0)
        for line in file:
            attempts += 1
            decoded_line = line.decode('utf-8', errors='ignore').strip()
            if ',' in decoded_line:
                hash_val, password_candidate = decoded_line.split(',', 1)
                if is_hash:
                    if hash_val == input_val:
                        found = True
                        password = password_candidate
                        break
                else:
                    if password_candidate == input_val:
                        found = True
                        password = password_candidate
                        break
            else:
                # fallback: treat as plain password list
                word = decoded_line
                if is_hash:
                    if check_hash(word, input_val, hash_type):
                        found = True
                        password = word
                        break
                else:
                    if word == input_val:
                        found = True
                        password = word
                        break
        else:
            with open("common_passwords.txt", "r", encoding="utf-8") as f:
                for line in f:
                    attempts += 1
                    word = line.strip()
                    if is_hash:
                        if check_hash(word, input_val, hash_type):
                            found = True
                            password = word
                            break
                    else:
                        if word == input_val:
                            found = True
                            password = word
                            break
    elif attack_type == "brute":
        chars = string.ascii_letters + string.digits + string.punctuation
        max_length = int(request.form.get("maxLength", 4))
        for length in range(1, max_length + 1):
            for guess in itertools.product(chars, repeat=length):
                attempts += 1
                guess_word = ''.join(guess)
                if is_hash:
                    if check_hash(guess_word, input_val, hash_type):
                        found = True
                        password = guess_word
                        break
                else:
                    if guess_word == input_val:
                        found = True
                        password = guess_word
                        break
            if found:
                break
    end = time.time()
    percent, suggestion = password_strength_analysis(input_val)
    if "user" in session:
        username = session["user"]
        user = users.get(username)
        if user is not None:
            from datetime import datetime
            if "history" not in user:
                user["history"] = []
            user["history"].append({
                "type": "Cracker",
                "input": input_val,
                "result": password if found else "Not found",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_users()
    return jsonify({
        "found": found,
        "password": password if found else "",
        "attempts": attempts,
        "time_taken": round(end - start, 4),
        "strength_percent": percent,
        "suggestion": suggestion
    })


@app.route("/check-strength", methods=["POST"])
def check_strength():
    data = request.get_json()
    password = data.get("password", "")
    score = 0
    remarks = []
    if len(password) >= 8:
        score += 1
    else:
        remarks.append("At least 8 characters.")
    if re.search(r"[a-z]", password):
        score += 1
    else:
        remarks.append("Add lowercase letters.")
    if re.search(r"[A-Z]", password):
        score += 1
    else:
        remarks.append("Add uppercase letters.")
    if re.search(r"\d", password):
        score += 1
    else:
        remarks.append("Add numbers.")
    if re.search(r"[!@#$%^&*()\-_=+{};:,<.>]", password):
        score += 1
    else:
        remarks.append("Add special characters.")
    if password.lower() in ['password', '123456', 'admin', 'letmein']:
        score = 1
        remarks = ["This is a commonly used password."]
    strength_level = ["Very Weak", "Weak", "Moderate", "Strong", "Very Strong", "Excellent"]
    return jsonify({
        "score": score,
        "remarks": remarks,
        "strength": strength_level[score]
    })

def password_strength_analysis(password):
    score = 0
    suggestions = []
    if len(password) >= 8:
        score += 1
    else:
        suggestions.append("Use at least 8 characters.")
    if re.search(r"[a-z]", password):
        score += 1
    else:
        suggestions.append("Add lowercase letters.")
    if re.search(r"[A-Z]", password):
        score += 1
    else:
        suggestions.append("Add uppercase letters.")
    if re.search(r"\d", password):
        score += 1
    else:
        suggestions.append("Add numbers.")
    if re.search(r"[!@#$%^&*()\-_=+{};:,<.>]", password):
        score += 1
    else:
        suggestions.append("Add special characters.")
    percent = int((score / 5) * 100)
    suggestion = " ".join(suggestions) if suggestions else "Strong password!"
    return percent, suggestion

@app.context_processor
def inject_globals():
    username = session.get("user")
    profile_pic = get_profile_pic(username) if username else None
    return dict(username=username, profile_pic=profile_pic)

@app.route("/add-history", methods=["POST"])
def add_history():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    data = request.get_json()
    username = session["user"]
    user = users.get(username)
    if user is not None:
        if "history" not in user:
            user["history"] = []
        from datetime import datetime
        user["history"].append({
            "type": data.get("type"),
            "input": data.get("input"),
            "result": data.get("result"),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_users()
        return jsonify({"success": True})
    return jsonify({"error": "User not found"}), 404

@app.route("/dashboard-data")
def dashboard_data():
    if "user" not in session:
        return jsonify([])
    username = session["user"]
    user = users.get(username, {})
    return jsonify(user.get("history", []))

if __name__ == "__main__":
    app.run(debug=True)