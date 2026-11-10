# DoJay
#### Video Demo:  <URL HERE>
#### Description:

**DoJay** is an enterprise-grade, multi-tenant SaaS platform engineered for live music venues, festivals, clubs, and event disc jockeys. It modernizes the live song request workflow by replacing chaotic verbal requests, handwritten paper napkins, and stage interruptions with a streamlined, real-time digital curation queue. Attendees scan a dynamic QR code on their mobile devices to access a dedicated event stage, search an official digital music catalog via the iTunes Search API, and submit verified song requests directly to the DJ's live console.

---

### Platform Architecture & Multi-Tenant Model

Traditional crowd request methods suffer from severe operational friction: performers are interrupted while beatmatching and mixing, illegible handwriting on napkins leads to errors, and attendees receive no confirmation regarding whether their request was seen or will be played. 

DoJay solves this problem at scale by implementing a multi-tenant relational architecture. Performers and venues register dedicated DJ accounts, create named stages or event rooms (such as "Main Stage", "Rooftop Lounge", or "VIP Afterparty"), and broadcast scannable QR codes. Attendees register frictionless guest accounts, join stages via unique alphanumeric codes or camera scans, and interact with a live queue dedicated strictly to that performance.

```text
       +-----------------------------------------------------------+
       |                       DoJay Cloud                         |
       +-----------------------------------------------------------+
                                     |
               +---------------------+---------------------+
               |                                           |
        [ DJ Operator ]                             [ Event Guests ]
               |                                           |
   +-----------------------+                   +-----------------------+
   | - Create Rooms/Stages |                   | - Scan Room QR Code   |
   | - Auto-generate QR    |                   | - Search iTunes API   |
   | - Live 5s Queue Poll  |                   | - Strict Track Select |
   | - Mark Tracks Played  |                   | - View Played History |
   +-----------------------+                   +-----------------------+
               \                                           /
                \---> [ SQLite Multi-Tenant DB ] <--------/
```

#### Database Schema Overview (`beatlink.db`)

1. **`users` Table**:
   * `id`: Integer primary key with autoincrement.
   * `username`: Case-insensitive unique handle.
   * `hash`: Secure salted password hash generated via Werkzeug security primitives.
   * `role`: Enum constraint enforcing either `'dj'` or `'guest'`. Governs application authorization and navigation workflows.

2. **`rooms` Table**:
   * `id`: Integer primary key.
   * `dj_id`: Foreign key referencing `users(id)` with cascading deletion.
   * `name`: Descriptive stage title (e.g., "Main Stage").
   * `unique_code`: Short, indexed alphanumeric identifier (e.g., `STAGE4`, `BEAT89`) used for routing and QR code generation.
   * `created_at`: UTC timestamp of room creation.

3. **`requests` Table**:
   * `id`: Integer primary key.
   * `room_id`: Foreign key referencing `rooms(id)` with cascading deletion.
   * `guest_id`: Foreign key referencing `users(id)` with cascading deletion.
   * `song_title`: Verified track name selected from the iTunes catalog.
   * `artist`: Verified artist name selected from the iTunes catalog.
   * `status`: Enum constraint enforcing `'pending'` or `'played'`.
   * `timestamp`: Automatic SQL timestamp documenting submission time.

---

### Core Feature Breakdown

#### 1. DJ Control Room (`/dj_dashboard`)
The performer's control center is designed for high-contrast visibility in dark club environments. 
* **Dynamic QR Code Generation**: Upon room creation, the platform utilizes Python's `qrcode` and `pillow` libraries to dynamically generate a high-resolution QR code pointing to the absolute URL `/room/<unique_code>`. The image is serialized into a base64 Data URI and rendered directly into the DOM without generating temporary files on disk.
* **Real-Time Queue Polling Engine**: A client-side JavaScript engine polls the authenticated REST endpoint `/api/room/<unique_code>/requests` every 5 seconds. Incoming requests are reconciled against in-memory state; new requests trigger subtle visual highlight transitions.
* **One-Click Playback Management**: Each request in the live feed features a "Mark as Played" trigger. When clicked, an asynchronous `POST` request is dispatched to `/api/played`. The backend updates the request record, and the UI animates the item out of the DOM while immediately recalculating pending and played metrics.

#### 2. Guest Stage Portal (`/guest_dashboard` & `/room/<unique_code>`)
Guests access a stage either by entering the 6-character room code on the dashboard or by scanning the DJ's booth QR code.
* **Strict Spotify Web API Autocomplete (Feature A)**: To eliminate spelling mistakes, joke submissions, and ensure robust discovery of local and international tracks, DoJay integrates directly with the Spotify Web API. As the user types into the search field, a debounced (320ms) asynchronous call queries our backend proxy (`/api/search?q=...`), which utilizes the Spotify Client Credentials flow to retrieve official tracks (configured for Market: GR with limit 15). A styled dropdown displays official album artwork, canonical track titles, and artist names. Guests **must** click a verified catalog result to populate hidden inputs and activate the submission button.
* **Played History & Repeat Prevention (Feature B)**: A dedicated section displays all tracks that have already been marked as `'played'` in the current room, accompanied by timestamps. This gives guests instant transparency into the DJ's set history and prevents duplicate song requests. Furthermore, the submission controller checks for pending duplicates in the database to prevent spam.

---

### Technical Design Choices

#### Why Spotify Web API with Server-Side Client Credentials Proxy
The search subsystem leverages the Spotify Web API via a secured server-side proxy (`/api/search`):
* **Comprehensive Regional Catalog Coverage**: The Spotify Web API (configured with `market=GR`) delivers superior search precision for local Greek and international tracks across mixed titles, aliases, and artist collabs, addressing the limitations of older public search endpoints.
* **Zero Client-Side Token Friction**: Rather than forcing attendees to authenticate with their personal Spotify accounts or exposing developer credentials in frontend code, the Flask backend manages the Client Credentials Flow using `requests` and cached server-side bearer tokens.
* **Protected Credential Management**: `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` are kept strictly server-side using `python-dotenv`, preventing API abuse and token leakage.

#### Why Client-Side Polling Over Persistent WebSockets
In physical event venues (such as subterranean clubs, metal festival stages, and crowded outdoor venues), mobile cellular connections and Wi-Fi networks frequently experience packet loss and brief drops. Persistent WebSocket connections require complex state-reconnection handshakes, ping/pong heartbeats, and dedicated persistent connection processes. Stateless HTTP polling via the modern JavaScript `fetch()` API fails gracefully: if a 5-second poll drops due to a momentary signal loss, the subsequent poll automatically retrieves the full queue state once connectivity resumes.

#### Why Flask and SQLite for Multi-Tenant Scaling
Flask's micro-framework architecture affords explicit control over routing, role verification decorators, and HTTP response headers. SQLite delivers exceptional single-file read/write speeds with zero network daemon latency, making it ideal for event sessions processing hundreds of transactions per evening.

---

### Project File Structure

```text
DoJay/
├── .env.example            # Environment variable configuration template
├── app.py                  # Core application controller, auth routes, Spotify proxy, and REST endpoints
├── beatlink.db             # Relational SQLite database
├── helpers.py              # Role decorators (@dj_required, @guest_required) and QR generator
├── init_db.py              # Database initialization and migration script
├── requirements.txt        # Production dependency specifications (with requests and python-dotenv)
├── schema.sql              # Relational DDL definitions and performance indexes
├── static/
│   └── styles.css          # Custom dark SaaS theme, glassmorphism, and live indicators
└── templates/
    ├── apology.html        # Commercial error presentation view
    ├── dj_dashboard.html   # Performer stage control room with live 5s polling
    ├── guest_dashboard.html# Guest stage discovery and direct code entry
    ├── layout.html         # Foundational SaaS layout with dynamic role navbar
    ├── login.html          # Authentication view
    ├── register.html       # Role-based account creation view
    └── room.html           # Guest stage interface with Spotify API autocomplete
```

---

### Installation & Deployment

1. **Clone and Navigate**:
   ```bash
   git clone <repository-url>
   cd DoJay
   ```

2. **Install Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Initialize Database**:
   ```bash
   python3 init_db.py
   ```

4. **Launch Application Server**:
   ```bash
   flask run
   ```
   The platform will be accessible at `http://127.0.0.1:5000/`.

---

### Acknowledgments & AI Usage

While the architectural blueprint, data models, and system design are original, artificial intelligence tools were utilized during development to assist with boilerplate code generation, verify iTunes API integration patterns, and refine responsive Bootstrap styling.
