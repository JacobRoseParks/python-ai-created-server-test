"""
app.py – Flask login backend
Designed for Azure App Service deployment (or local dev behind HTTPS).

Install deps:
    pip install flask flask-cors flask-limiter

Run locally:
    python app.py

For HTTPS in production, Azure App Service terminates TLS for you automatically.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__, static_folder=".")

# ── CORS (lock this down to your real domain in production) ──────────────────
CORS(app, origins=os.getenv("ALLOWED_ORIGINS", "*"))

# ── Rate-limit login attempts to 10 / minute per IP ─────────────────────────
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

# ── In-memory demo user store (swap for a real DB in production) ─────────────
USERS = {
    "demo@example.com": "password123",   # replace / remove before going live
}


# ── Serve the static login page ──────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "login.html")


# ── Login endpoint ───────────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}

    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    # Constant-time comparison to prevent timing attacks
    import hmac
    stored = USERS.get(email)
    if stored is None or not hmac.compare_digest(stored, password):
        return jsonify({"message": "Invalid email or password."}), 401

    # In production: create a signed JWT or server-side session here.
    return jsonify({"message": "Login successful."}), 200


# ── Health check (used by Azure App Service) ─────────────────────────────────
@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # Local dev only — Azure provides HTTPS termination automatically.
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=debug)
