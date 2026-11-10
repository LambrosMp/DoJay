import os
import time
import requests
from dotenv import load_dotenv
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import (
    apology,
    dj_required,
    generate_qr_base64,
    generate_room_code,
    guest_required,
    login_required,
)

# Load environment variables from .env file (e.g. SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
load_dotenv()

# In-memory Spotify token cache
spotify_token_cache = {
    "access_token": None,
    "expires_at": 0
}


def get_spotify_token():
    """
    Retrieve or refresh a Spotify Access Token using the Client Credentials Flow.
    Caches the token in memory until expiration.
    """
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        return None

    now = time.time()
    # Return cached token if valid for at least 60 more seconds
    if spotify_token_cache["access_token"] and spotify_token_cache["expires_at"] > now + 60:
        return spotify_token_cache["access_token"]

    try:
        auth_response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            timeout=5
        )
        if auth_response.status_code == 200:
            data = auth_response.json()
            spotify_token_cache["access_token"] = data["access_token"]
            spotify_token_cache["expires_at"] = now + data.get("expires_in", 3600)
            return spotify_token_cache["access_token"]
        else:
            print(f"Spotify token request failed [{auth_response.status_code}]: {auth_response.text}")
    except Exception as e:
        print("Error requesting Spotify access token:", e)

    return None


# Initialize Flask application
app = Flask(__name__)

# Secret key for session signing
app.secret_key = os.environ.get("SECRET_KEY", "dojay-commercial-saas-platform-key-2026")

# Configure session cookies
app.config["SESSION_PERMANENT"] = False

try:
    from flask_session import Session
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)
except ImportError:
    pass

# Initialize SocketIO for real-time WebSocket communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


@socketio.on("join_room")
def handle_join_room(data):
    """Subscribe a client connection to a specific event stage room."""
    room = data.get("room", "").strip().upper() if isinstance(data, dict) else ""
    if room:
        join_room(room)
        emit("status", {"msg": f"Connected to stage {room}"}, to=room)


@socketio.on("leave_room")
def handle_leave_room(data):
    """Unsubscribe a client connection from an event stage room."""
    room = data.get("room", "").strip().upper() if isinstance(data, dict) else ""
    if room:
        leave_room(room)


# Ensure responses are not cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Connect to SQLite database
db = SQL("postgresql://neondb_owner:npg_loSOMK7De4kN@ep-red-cell-berd34rb.c-9.us-east-2.aws.neon.tech/neondb?sslmode=require")

def init_db():
    """Ensure database schema and indexes exist."""
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('dj', 'guest'))
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            dj_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            unique_code TEXT NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (dj_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            room_id INTEGER NOT NULL,
            guest_id INTEGER NOT NULL,
            song_title TEXT NOT NULL,
            artist TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'played')),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
            FOREIGN KEY (guest_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_rooms_unique_code ON rooms(unique_code)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_rooms_dj_id ON rooms(dj_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_requests_room_status ON requests(room_id, status, timestamp)")


init_db()


# -----------------------------------------------------------------------------
# ROOT ROUTE & AUTHENTICATION
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    """Route traffic according to authentication state and role."""
    if session.get("user_id"):
        if session.get("role") == "dj":
            return redirect("/dj_dashboard")
        return redirect("/guest_dashboard")
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user as either a DJ or Guest."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")
        role = request.form.get("role", "").strip().lower()

        if not username:
            flash("Username is required.", "danger")
            return render_template("register.html")

        if not password:
            flash("Password is required.", "danger")
            return render_template("register.html")

        if password != confirmation:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        if role not in ("dj", "guest"):
            flash("Invalid account type selected.", "danger")
            return render_template("register.html")

        # Check for existing username
        existing = db.execute("SELECT id FROM users WHERE username = ?", username)
        if len(existing) > 0:
            flash("Username already taken. Please choose another.", "danger")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        user_id = db.execute(
            "INSERT INTO users (username, hash, role) VALUES (?, ?, ?)",
            username,
            password_hash,
            role,
        )

        session["user_id"] = user_id
        session["username"] = username
        session["role"] = role

        flash(f"Account created successfully. Welcome, {username}!", "success")
        if role == "dj":
            return redirect("/dj_dashboard")
        return redirect("/guest_dashboard")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate existing DJ or Guest."""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please provide both username and password.", "danger")
            return render_template("login.html")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid credentials.", "danger")
            return render_template("login.html")

        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        session["role"] = rows[0]["role"]

        if rows[0]["role"] == "dj":
            return redirect("/dj_dashboard")
        return redirect("/guest_dashboard")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Clear session and log user out."""
    session.clear()
    flash("You have been signed out.", "info")
    return redirect("/login")


# -----------------------------------------------------------------------------
# DJ FLOW (/dj_dashboard, Room Creation, Live Queue)
# -----------------------------------------------------------------------------

@app.route("/dj_dashboard")
@login_required
@dj_required
def dj_dashboard():
    """DJ control room: manage rooms, view QR code, monitor live queue."""
    dj_id = session["user_id"]

    # Fetch all rooms created by this DJ
    rooms = db.execute("SELECT * FROM rooms WHERE dj_id = ? ORDER BY id DESC", dj_id)

    # Determine selected room (via query param or newest room)
    selected_room = None
    requested_room_id = request.args.get("room_id")

    if requested_room_id:
        match = [r for r in rooms if str(r["id"]) == str(requested_room_id)]
        if match:
            selected_room = match[0]

    if not selected_room and rooms:
        selected_room = rooms[0]

    qr_code_base64 = None
    room_url = None
    pending_count = 0
    played_count = 0

    if selected_room:
        # Construct absolute room join URL for the QR code
        room_url = f"{request.host_url.rstrip('/')}/room/{selected_room['unique_code']}"
        try:
            qr_code_base64 = generate_qr_base64(room_url)
        except Exception as e:
            print("QR Generation error:", e)

        # Compute counts
        pending_count = db.execute(
            "SELECT COUNT(*) AS count FROM requests WHERE room_id = ? AND status = 'pending'",
            selected_room["id"],
        )[0]["count"]

        played_count = db.execute(
            "SELECT COUNT(*) AS count FROM requests WHERE room_id = ? AND status = 'played'",
            selected_room["id"],
        )[0]["count"]

    return render_template(
        "dj_dashboard.html",
        rooms=rooms,
        selected_room=selected_room,
        qr_code=qr_code_base64,
        room_url=room_url,
        pending_count=pending_count,
        played_count=played_count,
    )


@app.route("/dj/create_room", methods=["POST"])
@login_required
@dj_required
def create_room():
    """Create a new event room for the DJ."""
    name = request.form.get("name", "").strip()
    if not name:
        flash("Room name is required.", "danger")
        return redirect("/dj_dashboard")

    # Generate a unique room code
    unique_code = None
    for _ in range(10):
        candidate = generate_room_code(6)
        exists = db.execute("SELECT id FROM rooms WHERE unique_code = ?", candidate)
        if not exists:
            unique_code = candidate
            break

    if not unique_code:
        flash("Could not generate a unique room code. Please try again.", "danger")
        return redirect("/dj_dashboard")

    room_id = db.execute(
        "INSERT INTO rooms (dj_id, name, unique_code) VALUES (?, ?, ?)",
        session["user_id"],
        name,
        unique_code,
    )

    flash(f"Room '{name}' created with code {unique_code}.", "success")
    return redirect(f"/dj_dashboard?room_id={room_id}")


@app.route("/dj/close_room", methods=["POST"])
@login_required
@dj_required
def close_room():
    """
    Close and delete an active room and all its requests.
    Enforces that only the DJ owner of this room can trigger the action.
    """
    room_id = request.form.get("room_id")
    if not room_id:
        flash("Room ID is required to close the room.", "danger")
        return redirect("/dj_dashboard")

    # Authorize: ensure room exists and belongs to the current DJ
    room = db.execute("SELECT * FROM rooms WHERE id = ? AND dj_id = ?", room_id, session["user_id"])
    if not room:
        flash("Room not found or you are not authorized to close it.", "danger")
        return redirect("/dj_dashboard")

    room_name = room[0]["name"]

    # Delete all associated requests first
    db.execute("DELETE FROM requests WHERE room_id = ?", room_id)

    # Delete the room record
    db.execute("DELETE FROM rooms WHERE id = ? AND dj_id = ?", room_id, session["user_id"])

    flash(f"Room '{room_name}' has been successfully closed and deleted.", "info")
    return redirect("/dj_dashboard")


# -----------------------------------------------------------------------------
# GUEST FLOW (/guest_dashboard, /room/<unique_code>)
# -----------------------------------------------------------------------------

@app.route("/guest_dashboard", methods=["GET", "POST"])
@login_required
@guest_required
def guest_dashboard():
    """Guest portal: list active rooms, or join directly via room code."""
    if request.method == "POST":
        room_code = request.form.get("room_code", "").strip().upper()
        if not room_code:
            flash("Please enter a room code.", "danger")
            return redirect("/guest_dashboard")

        rows = db.execute("SELECT unique_code FROM rooms WHERE unique_code = ?", room_code)
        if not rows:
            flash(f"No active room found with code '{room_code}'.", "danger")
            return redirect("/guest_dashboard")

        return redirect(f"/room/{rows[0]['unique_code']}")

    # List active rooms with pending request count and DJ username
    rooms = db.execute("""
        SELECT
            r.id,
            r.name,
            r.unique_code,
            r.created_at,
            u.username AS dj_name,
            (SELECT COUNT(*) FROM requests req WHERE req.room_id = r.id AND req.status = 'pending') AS pending_count
        FROM rooms r
        JOIN users u ON r.dj_id = u.id
        ORDER BY r.id DESC
        LIMIT 50
    """)

    return render_template("guest_dashboard.html", rooms=rooms)


@app.route("/room/<unique_code>", methods=["GET", "POST"])
@login_required
def room_view(unique_code):
    """
    Room view:
    - Guests submit verified song requests.
    - Prevent duplicate queueing and re-requesting already played tracks.
    """
    rows = db.execute("""
        SELECT r.*, u.username AS dj_name
        FROM rooms r
        JOIN users u ON r.dj_id = u.id
        WHERE r.unique_code = ?
    """, unique_code.upper())

    if not rows:
        flash("Room not found or code invalid.", "danger")
        return redirect("/guest_dashboard" if session.get("role") == "guest" else "/dj_dashboard")

    room = rows[0]

    # Handle song request submission (Guests only)
    if request.method == "POST":
        if session.get("role") != "guest":
            flash("DJs cannot submit requests to this room. Please use a Guest account.", "warning")
            return redirect(f"/room/{unique_code}")

        song_title = request.form.get("song_title", "").strip()
        artist = request.form.get("artist", "").strip()

        # Strict validation: Title and artist must be provided from Spotify selection
        if not song_title or not artist:
            flash("Please select a valid song from the Spotify search dropdown.", "danger")
            return redirect(f"/room/{unique_code}")

        # Anti-Spam Rate Limiting: 1 request every 3 minutes (180 seconds) per room
        recent_request = db.execute("""
            SELECT (strftime('%s', 'now') - strftime('%s', timestamp)) AS diff
            FROM requests
            WHERE room_id = ? AND guest_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, room["id"], session["user_id"])

        if recent_request and recent_request[0]["diff"] is not None and recent_request[0]["diff"] < 180:
            flash("Please wait 3 minutes before requesting another track to avoid spamming the DJ.", "warning")
            return redirect(f"/room/{unique_code}")

        # Check if track has already been played tonight in this room
        already_played = db.execute("""
            SELECT id FROM requests
            WHERE room_id = ? AND LOWER(song_title) = LOWER(?) AND LOWER(artist) = LOWER(?) AND status = 'played'
        """, room["id"], song_title, artist)

        if already_played:
            flash("This track has already been played tonight!", "warning")
            return redirect(f"/room/{unique_code}")

        # Global duplicate queue check (pending requests from ANY user in this room)
        in_queue = db.execute("""
            SELECT id FROM requests
            WHERE room_id = ? AND LOWER(song_title) = LOWER(?) AND LOWER(artist) = LOWER(?) AND status = 'pending'
        """, room["id"], song_title, artist)

        if in_queue:
            flash("Someone has already requested this track. It's currently in the DJ's queue!", "warning")
            return redirect(f"/room/{unique_code}")

        new_req_id = db.execute("""
            INSERT INTO requests (room_id, guest_id, song_title, artist, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, room["id"], session["user_id"], song_title, artist)

        # Broadcast real-time WebSocket event to DJ console
        try:
            socketio.emit("new_request", {
                "id": new_req_id,
                "song_title": song_title,
                "artist": artist,
                "guest_name": session.get("username", "Guest"),
                "time_str": "Just now",
                "room": unique_code.upper()
            }, to=unique_code.upper())
        except Exception as e:
            print("SocketIO emit error:", e)

        flash(f"'{song_title}' by {artist} submitted to DJ {room['dj_name']}!", "success")
        return redirect(f"/room/{unique_code}")

    # Check if guest has pending requests in this room
    my_pending = db.execute("""
        SELECT song_title, artist, strftime('%H:%M', timestamp) AS time_str
        FROM requests
        WHERE room_id = ? AND guest_id = ? AND status = 'pending'
        ORDER BY timestamp ASC
    """, room["id"], session["user_id"])

    return render_template(
        "room.html",
        room=room,
        my_pending=my_pending,
    )


# -----------------------------------------------------------------------------
# REST API (Live Polling & State Management)
# -----------------------------------------------------------------------------

@app.route("/api/room/<unique_code>/requests", methods=["GET"])
@login_required
def get_room_requests(unique_code):
    """Return JSON array of pending requests for a specific room."""
    rows = db.execute("SELECT id FROM rooms WHERE unique_code = ?", unique_code.upper())
    if not rows:
        return jsonify({"error": "Room not found"}), 404

    room_id = rows[0]["id"]
    requests = db.execute("""
        SELECT
            r.id,
            r.song_title,
            r.artist,
            r.status,
            strftime('%H:%M:%S', r.timestamp) AS time_str,
            r.timestamp,
            u.username AS guest_name
        FROM requests r
        JOIN users u ON r.guest_id = u.id
        WHERE r.room_id = ? AND r.status = 'pending'
        ORDER BY r.timestamp ASC
    """, room_id)

    return jsonify(requests)


@app.route("/api/room/<unique_code>/played", methods=["GET"])
@login_required
def get_room_played(unique_code):
    """Return JSON array of recently played tracks for a room (Feature B polling)."""
    rows = db.execute("SELECT id FROM rooms WHERE unique_code = ?", unique_code.upper())
    if not rows:
        return jsonify({"error": "Room not found"}), 404

    room_id = rows[0]["id"]
    played = db.execute("""
        SELECT
            r.id,
            r.song_title,
            r.artist,
            strftime('%H:%M', r.timestamp) AS time_str,
            u.username AS guest_name
        FROM requests r
        JOIN users u ON r.guest_id = u.id
        WHERE r.room_id = ? AND r.status = 'played'
        ORDER BY r.timestamp DESC
        LIMIT 25
    """, room_id)

    return jsonify(played)


@app.route("/api/played", methods=["POST"])
@login_required
@dj_required
def mark_played():
    """Mark a song request as played. Only permitted by the room's DJ."""
    data = request.get_json(silent=True) or request.form
    request_id = data.get("id")

    if not request_id:
        return jsonify({"success": False, "error": "Request ID required"}), 400

    # Ensure the request belongs to a room owned by this DJ
    verification = db.execute("""
        SELECT r.id, r.room_id
        FROM requests r
        JOIN rooms rm ON r.room_id = rm.id
        WHERE r.id = ? AND rm.dj_id = ?
    """, request_id, session["user_id"])

    if not verification:
        return jsonify({"success": False, "error": "Unauthorized action"}), 403

    room_id = verification[0]["room_id"]
    db.execute("UPDATE requests SET status = 'played' WHERE id = ?", request_id)

    pending_count = db.execute(
        "SELECT COUNT(*) AS count FROM requests WHERE room_id = ? AND status = 'pending'",
        room_id,
    )[0]["count"]

    played_count = db.execute(
        "SELECT COUNT(*) AS count FROM requests WHERE room_id = ? AND status = 'played'",
        room_id,
    )[0]["count"]

    # Broadcast real-time WebSocket update
    room_code_rows = db.execute("SELECT unique_code FROM rooms WHERE id = ?", room_id)
    if room_code_rows:
        room_code = room_code_rows[0]["unique_code"]
        socketio.emit("request_played", {
            "id": request_id,
            "pending_count": pending_count,
            "played_count": played_count,
            "room": room_code
        }, to=room_code)

    return jsonify({
        "success": True,
        "message": "Track marked as played.",
        "id": request_id,
        "pending_count": pending_count,
        "played_count": played_count,
    })


@app.route("/api/reject", methods=["POST"])
@login_required
@dj_required
def reject_request():
    """Delete a song request entirely. Only permitted by the room's DJ."""
    data = request.get_json(silent=True) or request.form
    request_id = data.get("id")

    if not request_id:
        return jsonify({"success": False, "error": "Request ID required"}), 400

    # Επιβεβαίωση ότι το τραγούδι ανήκει σε δωμάτιο αυτού του DJ
    verification = db.execute("""
        SELECT r.id, r.room_id
        FROM requests r
        JOIN rooms rm ON r.room_id = rm.id
        WHERE r.id = ? AND rm.dj_id = ?
    """, request_id, session["user_id"])

    if not verification:
        return jsonify({"success": False, "error": "Unauthorized action"}), 403

    room_id = verification[0]["room_id"]

    # Διαγραφή από τη βάση
    db.execute("DELETE FROM requests WHERE id = ?", request_id)

    # Υπολογισμός νέου συνόλου αναμονής
    pending_count = db.execute(
        "SELECT COUNT(*) AS count FROM requests WHERE room_id = ? AND status = 'pending'",
        room_id,
    )[0]["count"]

    # Broadcast real-time WebSocket update
    room_code_rows = db.execute("SELECT unique_code FROM rooms WHERE id = ?", room_id)
    if room_code_rows:
        room_code = room_code_rows[0]["unique_code"]
        socketio.emit("request_rejected", {
            "id": request_id,
            "pending_count": pending_count,
            "room": room_code
        }, to=room_code)

    return jsonify({
        "success": True,
        "message": "Track rejected.",
        "id": request_id,
        "pending_count": pending_count
    })


# -----------------------------------------------------------------------------
# SPOTIFY WEB API SEARCH ENDPOINT
# -----------------------------------------------------------------------------

@app.route("/api/search", methods=["GET"])
@login_required
def search_spotify():
    """
    Search Spotify Web API for tracks (market: GR, limit: 15).
    Uses the Client Credentials flow via server-side token management.
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    token = get_spotify_token()
    if not token:
        return jsonify({
            "error": "Spotify credentials missing or unconfigured. Please define SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file."
        }), 500

    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": query,
        "type": "track",
        "market": "GR"

    }

    try:
        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers=headers,
            params=params,
            timeout=5
        )

        if response.status_code != 200:
            print("❌ SPOTIFY ΛΕΕΙ:", response.text)
            return jsonify({
                "error": f"Spotify API error ({response.status_code})"
            }), response.status_code

        data = response.json()
        items = data.get("tracks", {}).get("items", [])
        results = []

        for item in items:
            track_name = item.get("name", "")
            artists = ", ".join([a.get("name", "") for a in item.get("artists", [])])
            album_images = item.get("album", {}).get("images", [])
            # Medium thumbnail (images[1] or images[0])
            artwork_url = album_images[1]["url"] if len(album_images) > 1 else (album_images[0]["url"] if album_images else "")

            results.append({
                "id": item.get("id"),
                "track_name": track_name,
                "artist_name": artists,
                "artwork_url": artwork_url,
                "preview_url": item.get("preview_url")
            })

        return jsonify(results)

    except Exception as e:
        print("Spotify search endpoint exception:", e)
        return jsonify({"error": "Failed to connect to Spotify search service."}), 500


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
