import base64
import io
import random
import string
from functools import wraps
from flask import redirect, render_template, session
import qrcode


def login_required(f):
    """Ensure user is logged in before accessing route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def dj_required(f):
    """Ensure authenticated user has the 'dj' role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        if session.get("role") != "dj":
            return redirect("/guest_dashboard")
        return f(*args, **kwargs)
    return decorated_function


def guest_required(f):
    """Ensure authenticated user has the 'guest' role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        if session.get("role") != "guest":
            return redirect("/dj_dashboard")
        return f(*args, **kwargs)
    return decorated_function


def generate_qr_base64(data_url: str) -> str:
    """Generate a high-contrast QR code image as a base64 encoded string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(data_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0a0e1a", back_color="#ffffff")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


def generate_room_code(length: int = 6) -> str:
    """Generate a clean, readable alphanumeric room code."""
    chars = string.ascii_uppercase + string.digits
    # Avoid ambiguous characters (0, O, 1, I)
    clean_chars = [c for c in chars if c not in "0OI1"]
    return "".join(random.choices(clean_chars, k=length))


def apology(message: str, code: int = 400):
    """Render friendly error message."""
    return render_template("apology.html", top=code, bottom=message), code
