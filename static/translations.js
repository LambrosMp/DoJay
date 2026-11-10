/**
 * BeatLink / DoJay - Dynamic Client-side Translation Engine
 * Supports seamless toggling between English (EN) and Greek (EL).
 */

(function () {
    const translations = {
        en: {
            // Navbar
            brand_name: "DoJay",
            nav_dj_control: "DJ Control Room",
            nav_event_rooms: "Event Rooms",
            nav_sign_out: "Sign Out",
            nav_sign_in: "Sign In",
            nav_get_started: "Get Started",
            lang_label: "EN",

            // Footer
            footer_copyright: "© 2026 <strong>DoJay.</strong> All rights reserved.",
            footer_desc: "Enterprise real-time crowd music curation for venues, festivals, and performers.",

            // Guest Dashboard
            guest_portal: "Guest Portal",
            find_your_stage: "Find Your Stage",
            guest_stage_desc: "Enter the stage code provided by your event DJ at the venue to join and request songs directly from the crowd.",
            have_room_code: "Have a 6-Character Room Code?",
            room_code_placeholder: "e.g. STAGE4",
            enter_btn: "Enter",
            active_event_rooms: "Active Event Rooms",
            stages_online: "Stages Online",
            no_active_rooms: "No Active Rooms Found",
            no_active_rooms_desc: "No stages are currently broadcasting. Check back soon or enter a room code provided by your DJ.",
            in_queue: "in queue",
            hosted_by_dj: "Hosted by DJ",
            code_required: "Code Required",
            in_person_notice: "In-Person Stage • Enter Code Above",

            // DJ Dashboard
            dj_control_room: "DJ Control Room",
            dj_desc: "Manage event stages, display room QR codes, and curate incoming crowd requests in real-time.",
            create_room: "Create Room",
            close_room: "Close Room",
            live_queue: "LIVE QUEUE",
            no_rooms_title: "No Active Event Rooms",
            no_rooms_desc: "Create your first room (e.g. \"Main Stage\", \"VIP Lounge\", or \"Afterparty\") to generate a live QR code and start accepting crowd requests.",
            create_first_room: "Create Your First Room",
            switch_room: "Switch Active Room",
            active_stage: "Active Stage",
            created: "Created",
            share_code_qr: "Share this code or QR code with guests",
            copy_code: "Copy Code",
            copied: "Copied!",
            open_room: "Open Room",
            qr_scan_notice: "Guests scan this QR to open the live request portal",
            qr_unavailable: "QR Code unavailable",
            stat_in_queue: "In Queue",
            stat_played: "Played",
            incoming_requests: "Incoming Song Requests",
            updated_now: "Updated just now",
            connecting_feed: "Connecting to live booth feed...",
            queue_clear: "Queue is Clear",
            queue_clear_desc: "No pending requests in this room right now. Display the QR code for attendees to start requesting tracks.",
            mark_played: "Mark Played",
            reject: "Reject",

            // Modals
            modal_create_title: "Create Event Room",
            modal_room_name: "Room / Stage Name",
            modal_room_placeholder: "e.g. Main Stage, Rooftop Lounge, Wedding Reception",
            modal_room_hint: "A unique room code and scannable QR code will be generated automatically.",
            cancel: "Cancel",
            generate_room: "Generate Room",

            // Close Room Modal
            close_room_modal_title: "Close Room",
            close_room_confirm_msg: "Are you sure you want to close this room? This will end the session and delete all requests.",
            room_to_close: "Room to close:",
            confirm_close_btn: "Confirm & Close Room",

            // Room / Guest View
            live_stage: "Live Stage",
            hosted_by: "Hosted by",
            share_link: "Share Link",
            all_rooms: "All Rooms",
            drop_track_title: "Drop a Track to the DJ",
            drop_track_desc: "Search the Spotify catalog (Market: GR) and select a verified track.",
            search_song_artist: "Search Song or Artist",
            search_placeholder: "Type title or artist (e.g. Blinding Lights, Drake)",
            search_hint: "You must select a track from the suggestions to submit.",
            submit_request: "Submit Song Request",
            your_pending_requests: "Your Pending Requests for this Stage",
            badge_pending: "Pending",
            no_results_found: "No matching songs found on Spotify (Market: GR).",
            err_search: "Error searching Spotify. Please try again.",

            // Auth
            welcome_back: "Welcome Back",
            login_subtitle: "Sign in to manage your stage or submit song requests",
            username: "Username",
            username_placeholder: "Enter your username",
            password: "Password",
            password_placeholder: "Enter your password",
            sign_in_btn: "Sign In",
            new_to_dojay: "New to DoJay?",
            create_an_account: "Create an Account",
            join_dojay: "Join DoJay",
            register_subtitle: "Create an account to start managing live stages or requesting tracks",
            confirm_password: "Confirm Password",
            confirm_password_placeholder: "Re-enter your password",
            account_type: "Account Type",
            role_guest_title: "Guest / Attendee",
            role_guest_desc: "Submit song requests at venues and stages.",
            role_dj_title: "DJ / Performer",
            role_dj_desc: "Create rooms, display QR codes, and curate requests.",
            create_account_btn: "Create Account",
            already_have_account: "Already have an account?"
        },
        el: {
            // Navbar
            brand_name: "DoJay",
            nav_dj_control: "Κονσόλα DJ",
            nav_event_rooms: "Αίθουσες Εκδηλώσεων",
            nav_sign_out: "Αποσύνδεση",
            nav_sign_in: "Σύνδεση",
            nav_get_started: "Εγγραφή",
            lang_label: "ΕΛ",

            // Footer
            footer_copyright: "© 2026 <strong>DoJay.</strong> Με την επιφύλαξη παντός δικαιώματος.",
            footer_desc: "Επαγγελματική διαχείριση μουσικών αιτημάτων σε πραγματικό χρόνο για χώρους εκδηλώσεων, φεστιβάλ και DJs.",

            // Guest Dashboard
            guest_portal: "Πύλη Επισκεπτών",
            find_your_stage: "Βρείτε τη Σκηνή σας",
            guest_stage_desc: "Εισαγάγετε τον κωδικό σκηνής που σας δόθηκε από τον DJ για να συνδεθείτε και να ζητήσετε τραγούδια απευθείας.",
            have_room_code: "Έχετε 6-ψήφιο Κωδικό Αίθουσας;",
            room_code_placeholder: "π.χ. STAGE4",
            enter_btn: "Είσοδος",
            active_event_rooms: "Ενεργές Αίθουσες Εκδηλώσεων",
            stages_online: "Σκηνές Online",
            no_active_rooms: "Δεν Βρέθηκαν Ενεργές Αίθουσες",
            no_active_rooms_desc: "Δεν υπάρχουν ενεργές σκηνές αυτή τη στιγμή. Δοκιμάστε ξανά σύντομα ή εισαγάγετε τον κωδικό από τον DJ σας.",
            in_queue: "στην ουρά",
            hosted_by_dj: "Διοργάνωση από DJ",
            code_required: "Απαιτείται Κωδικός",
            in_person_notice: "Σκηνή Χώρου • Εισαγάγετε τον Κωδικό Παραπάνω",

            // DJ Dashboard
            dj_control_room: "Κονσόλα DJ",
            dj_desc: "Διαχειριστείτε τις σκηνές, προβάλετε κωδικούς QR και επιμεληθείτε τα αιτήματα κοινού σε πραγματικό χρόνο.",
            create_room: "Δημιουργία Αίθουσας",
            close_room: "Κλείσιμο Αίθουσας",
            live_queue: "ΖΩΝΤΑΝΗ ΟΥΡΑ",
            no_rooms_title: "Δεν Υπάρχουν Ενεργές Αίθουσες",
            no_rooms_desc: "Δημιουργήστε την πρώτη σας αίθουσα (π.χ. \"Κεντρική Σκηνή\", \"VIP Lounge\") για να δημιουργήσετε QR code και να δέχεστε αιτήματα.",
            create_first_room: "Δημιουργήστε την Πρώτη σας Αίθουσα",
            switch_room: "Αλλαγή Ενεργής Αίθουσας",
            active_stage: "Ενεργή Σκηνή",
            created: "Δημιουργήθηκε",
            share_code_qr: "Μοιραστείτε αυτόν τον κωδικό ή το QR code με τους καλεσμένους",
            copy_code: "Αντιγραφή Κωδικού",
            copied: "Αντιγράφηκε!",
            open_room: "Άνοιγμα Αίθουσας",
            qr_scan_notice: "Οι καλεσμένοι σκανάρουν αυτό το QR για να ανοίξουν την πύλη αιτημάτων",
            qr_unavailable: "Το QR Code δεν είναι διαθέσιμο",
            stat_in_queue: "Στην Ουρά",
            stat_played: "Παίχτηκαν",
            incoming_requests: "Εισερχόμενα Αιτήματα Τραγουδιών",
            updated_now: "Ενημερώθηκε μόλις τώρα",
            connecting_feed: "Σύνδεση με τη ζωντανή ροή...",
            queue_clear: "Η Ουρά είναι Άδεια",
            queue_clear_desc: "Δεν υπάρχουν αιτήματα σε αναμονή. Προβάλετε το QR code για να ξεκινήσουν οι παραγγελίες.",
            mark_played: "Ολοκληρώθηκε",
            reject: "Απόρριψη",

            // Modals
            modal_create_title: "Δημιουργία Αίθουσας Εκδήλωσης",
            modal_room_name: "Όνομα Αίθουσας / Σκηνής",
            modal_room_placeholder: "π.χ. Κεντρική Σκηνή, VIP Lounge, Δεξίωση Γάμου",
            modal_room_hint: "Ένας μοναδικός κωδικός και QR code θα δημιουργηθούν αυτόματα.",
            cancel: "Ακύρωση",
            generate_room: "Δημιουργία Αίθουσας",

            // Close Room Modal
            close_room_modal_title: "Κλείσιμο Αίθουσας",
            close_room_confirm_msg: "Είστε σίγουροι ότι θέλετε να κλείσετε αυτή την αίθουσα; Αυτό θα τερματίσει τη συνεδρία και θα διαγράψει όλα τα αιτήματα.",
            room_to_close: "Αίθουσα προς κλείσιμο:",
            confirm_close_btn: "Επιβεβαίωση & Κλείσιμο",

            // Room / Guest View
            live_stage: "Ζωντανή Σκηνή",
            hosted_by: "Διοργάνωση από",
            share_link: "Κοινοποίηση Συνδέσμου",
            all_rooms: "Όλες οι Αίθουσες",
            drop_track_title: "Στείλτε ένα Τραγούδι στον DJ",
            drop_track_desc: "Αναζητήστε στον κατάλογο Spotify (Αγορά: GR) και επιλέξτε ένα έγκυρο τραγούδι.",
            search_song_artist: "Αναζήτηση Τραγουδιού ή Καλλιτέχνη",
            search_placeholder: "Πληκτρολογήστε τίτλο ή καλλιτέχνη (π.χ. Blinding Lights, Drake)",
            search_hint: "Πρέπει να επιλέξετε ένα τραγούδι από τις προτάσεις για υποβολή.",
            submit_request: "Υποβολή Αιτήματος Τραγουδιού",
            your_pending_requests: "Τα Αιτήματά σας σε Αναμονή",
            badge_pending: "Σε Αναμονή",
            no_results_found: "Δεν βρέθηκαν σχετικά τραγούδια στο Spotify (Market: GR).",
            err_search: "Σφάλμα αναζήτησης Spotify. Παρακαλώ δοκιμάστε ξανά.",

            // Auth
            welcome_back: "Καλώς Ήρθατε Πάλι",
            login_subtitle: "Συνδεθείτε για να διαχειριστείτε τη σκηνή σας ή να ζητήσετε τραγούδια",
            username: "Όνομα Χρήστη",
            username_placeholder: "Εισαγάγετε το όνομα χρήστη",
            password: "Κωδικός Πρόσβασης",
            password_placeholder: "Εισαγάγετε τον κωδικό πρόσβασης",
            sign_in_btn: "Σύνδεση",
            new_to_dojay: "Νέος στο DoJay;",
            create_an_account: "Δημιουργία Λογαριασμού",
            join_dojay: "Εγγραφή στο DoJay",
            register_subtitle: "Δημιουργήστε λογαριασμό για να διαχειρίζεστε σκηνές ή να ζητάτε τραγούδια",
            confirm_password: "Επιβεβαίωση Κωδικού",
            confirm_password_placeholder: "Επανεισάγετε τον κωδικό πρόσβασης",
            account_type: "Τύπος Λογαριασμού",
            role_guest_title: "Επισκέπτης / Θαμώνας",
            role_guest_desc: "Υποβολή αιτημάτων τραγουδιών σε χώρους και σκηνές.",
            role_dj_title: "DJ / Καλλιτέχνης",
            role_dj_desc: "Δημιουργία αιθουσών, προβολή QR codes και επιμέλεια αιτημάτων.",
            create_account_btn: "Δημιουργία Λογαριασμού",
            already_have_account: "Έχετε ήδη λογαριασμό;"
        }
    };

    function getLanguage() {
        const stored = localStorage.getItem("beatlink_lang");
        return stored === "el" ? "el" : "en";
    }

    function setLanguage(lang) {
        const targetLang = lang === "el" ? "el" : "en";
        localStorage.setItem("beatlink_lang", targetLang);
        applyTranslations(targetLang);
    }

    function t(key, lang = getLanguage()) {
        const dict = translations[lang] || translations.en;
        return dict[key] || translations.en[key] || key;
    }

    function applyTranslations(lang = getLanguage(), root = document) {
        document.documentElement.lang = lang;

        // Update Toggle Button UI (Flag & label)
        const flagEl = document.getElementById("langFlag");
        const codeEl = document.getElementById("langCode");
        const toggleBtn = document.getElementById("langToggleBtn");

        if (flagEl) {
            flagEl.textContent = lang === "el" ? "🇬🇷" : "🇬🇧";
        }
        if (codeEl) {
            codeEl.textContent = lang === "el" ? "ΕΛ" : "EN";
        }
        if (toggleBtn) {
            toggleBtn.title = lang === "el" ? "Εναλλαγή σε English (🇬🇧)" : "Switch to Ελληνικά (🇬🇷)";
            toggleBtn.setAttribute("aria-label", toggleBtn.title);
        }

        // Translate text nodes
        root.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            const val = t(key, lang);
            if (val) {
                if (el.getAttribute("data-i18n-html") === "true") {
                    el.innerHTML = val;
                } else {
                    el.textContent = val;
                }
            }
        });

        // Translate input placeholders
        root.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
            const key = el.getAttribute("data-i18n-placeholder");
            const val = t(key, lang);
            if (val) {
                el.placeholder = val;
            }
        });

        // Translate titles / tooltips
        root.querySelectorAll("[data-i18n-title]").forEach(el => {
            const key = el.getAttribute("data-i18n-title");
            const val = t(key, lang);
            if (val) {
                el.title = val;
            }
        });

        // Broadcast event for dynamic components (like live queue)
        window.dispatchEvent(new CustomEvent("languageChanged", { detail: { lang } }));
    }

    function toggleLanguage() {
        const current = getLanguage();
        const next = current === "en" ? "el" : "en";
        setLanguage(next);
    }

    // Expose globally
    window.i18n = {
        getLanguage,
        setLanguage,
        toggleLanguage,
        applyTranslations,
        t
    };

    // Initialize on page load
    function init() {
        applyTranslations(getLanguage());

        const toggleBtn = document.getElementById("langToggleBtn");
        if (toggleBtn) {
            toggleBtn.removeEventListener("click", toggleLanguage);
            toggleBtn.addEventListener("click", toggleLanguage);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
