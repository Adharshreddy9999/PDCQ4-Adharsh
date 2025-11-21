import os
import datetime
import pytz
import requests
import base64
from flask import Flask, session, redirect, url_for, request, render_template_string, flash
from google_auth_oauthlib.flow import Flow

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
app = Flask(__name__)
app.secret_key = os.urandom(24)

GOOGLE_CLIENT_ID = "929567193096-lp85cd9f9ifkqau2dsdgvosm2i4vnhl8.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"

CLIENT_CONFIG = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "project_id": "local-flask-app",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uris": ["http://localhost:5000/callback"]
    }
}

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email"
]

GOOGLE_LOGO_LOCAL = "static/google_logo.png"
PROFILE_FALLBACK_LOCAL = "/mnt/data/IMG_2150E99A-AAA1-4BEF-9BBF-3FCD829FAEDA.jpeg"

def file_to_data_url(path):
    try:
        with open(path, "rb") as f:
            b = f.read()
        return "data:image/png;base64," + base64.b64encode(b).decode("ascii")
    except:
        return ""

def indian_time_str():
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.datetime.now(tz).strftime("%d %b %Y, %I:%M:%S %p %Z")

def get_flow():
    redirect_uri = url_for("callback", _external=True)
    return Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES, redirect_uri=redirect_uri)

def fetch_userinfo(token):
    try:
        r = requests.get("https://www.googleapis.com/oauth2/v2/userinfo",
                         headers={"Authorization": f"Bearer {token}"}, timeout=8)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

BASE = "FORMULAQSOLUTIONS"

def generate_design(n):
    s = "FORMULAQSOLUTIONS"
    slen = len(s)
    mid = n // 2
    lines = []
    for row in range(n):
        skip = abs(mid - row)
        width = n - 2 * skip
        if width <= slen:
            start = (slen - width) // 2
            part = s[start:start+width]
        else:
            reps = (width // slen) + 2
            long_s = s * reps
            start = (len(long_s) - width) // 2
            part = long_s[start:start+width]
        if row % 2 == 0:
            line = part
        else:
            if width > 2:
                line = part[0] + '-' * (width - 2) + part[-1]
            else:
                line = part
        lines.append(line.center(n))
    return lines

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    body{font-family:Segoe UI,Roboto,Arial,sans-serif;background:#f6f7f9;margin:0;padding:32px;color:#222}
    .wrap{max-width:960px;margin:0 auto}
    h1{margin:0 0 10px 0;font-size:28px}
    .card{background:#fff;padding:20px;border:1px solid #e1e1e1;border-radius:6px}
    .gbtn{display:inline-flex;gap:8px;align-items:center;padding:8px 12px;border-radius:6px;border:1px solid #ddd;background:#fff;text-decoration:none;color:#333;font-weight:600}
    .gbtn img{width:20px;height:20px}
    .profile-box{display:flex;gap:18px;align-items:center;margin-top:18px;padding:18px;border:1px solid #eee;border-radius:6px;background:#fff}
    .avatar{width:96px;height:96px;border-radius:50%;overflow:hidden;border:3px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.06)}
    .avatar img{width:100%;height:100%;object-fit:cover}
    .hello{font-size:26px;font-weight:700;color:#243447}
    .email{margin-top:8px;font-size:18px;color:#243447}
    .time{margin-top:6px;color:#666}
    .form-row{margin-top:12px;display:flex;gap:8px;align-items:center}
    input[type=number]{padding:8px;border-radius:6px;border:1px solid #ddd;width:140px}
    button.primary{background:#1a73e8;color:#fff;border:none;padding:8px 14px;border-radius:6px;cursor:pointer;font-weight:700}
    .design{font-family:Courier,monospace;white-space:pre;text-align:left;margin-top:22px;color:#111}
    .info{margin-top:12px;color:#666;padding:14px;border:1px dashed #e9e9e9;border-radius:6px}
    ul.flash{color:#c44;margin-top:10px}
  </style>
</head>

<body>

    <div class="wrap">
        {% if user %}
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:18px;">
            <img src="{{ google_logo }}" alt="G" style="width:28px;height:28px;">
            <span style="font-size:18px;font-weight:600;color:#222;">Signed in</span>
        </div>
        {% endif %}

    <div class="card">

      {% if not user %}
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:15px;">
        <a class="gbtn" href="{{ url_for('login') }}">
          <img src="{{ google_logo }}" alt="G">
          Sign in with Google
        </a>
      </div>
      {% endif %}

      {% if user %}
      <div class="profile-box">
        <div class="avatar"><img src="{{ profile_src }}"></div>
        <div style="flex:1">
          <div style="display:flex;align-items:center;gap:10px;">
            <div class="hello">Hello {{ user.name }}</div>
            <a href="{{ url_for('logout') }}" style="color:#1a73e8;text-decoration:none;font-weight:600;">[Sign out]</a>
          </div>
          <div class="email">You are signed in with the email <strong>{{ user.email }}</strong></div>
          <div class="time">Current Indian time: <strong>{{ indian_time }}</strong></div>

          <form method="post" action="{{ url_for('display') }}">
            <div class="form-row">
              <label style="color:#666">Number of Lines</label>
              <input type="number" name="num_lines" min="1" max="100" required value="{{ last_num }}">
              <button class="primary" type="submit">Display</button>
            </div>
          </form>
        </div>
      </div>
      {% endif %}

      {% if lines %}
      <div class="design">
{% for l in lines %}{{ l }}
{% endfor %}
      </div>
      {% endif %}

      {% with messages = get_flashed_messages() %}
      {% if messages %}
      <ul class="flash">
        {% for m in messages %}<li>{{ m }}</li>{% endfor %}
      </ul>
      {% endif %}
      {% endwith %}

    </div>
  </div>
</body>
</html>
"""

@app.route("/")
def index():
    user = session.get("user")
    if user and user.get("picture"):
        profile_src = user.get("picture")
    else:
        profile_src = PROFILE_FALLBACK_LOCAL

    google_logo = file_to_data_url(GOOGLE_LOGO_LOCAL)

    return render_template_string(
        HTML,
        user=user,
        profile_src=profile_src,
        google_logo=google_logo,
        indian_time=indian_time_str(),
        lines=session.get("generated_lines", []),
        last_num=session.get("last_num", "")
    )

@app.route("/login")
def login():
    flow = get_flow()
    auth_url, state = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="true")
    session["state"] = state
    return redirect(auth_url)

@app.route("/callback")
def callback():
    flow = get_flow()
    try:
        flow.fetch_token(authorization_response=request.url)
    except:
        flash("Authentication failed.")
        return redirect(url_for("index"))
    info = fetch_userinfo(flow.credentials.token)
    if not info:
        flash("Failed to fetch user info.")
        return redirect(url_for("index"))
    session["user"] = {
        "name": info.get("name", info.get("email")),
        "email": info.get("email"),
        "picture": info.get("picture")
    }
    session.pop("generated_lines", None)
    session.pop("last_num", None)
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    flash("You have signed out.")
    return redirect(url_for("index"))

@app.route("/display", methods=["POST"])
def display():
    if "user" not in session:
        flash("Please sign in first.")
        return redirect(url_for("index"))
    try:
        n = int(request.form.get("num_lines", ""))
    except:
        flash("Enter a valid number.")
        return redirect(url_for("index"))
    n = max(1, min(100, n))
    session["last_num"] = str(n)
    session["generated_lines"] = generate_design(n)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
