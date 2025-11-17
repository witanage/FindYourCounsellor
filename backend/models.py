import bcrypt
from datetime import datetime, timedelta
import json
from backend.database import Database

class User:
    @staticmethod
    def create(email, password, first_name, last_name, user_type, phone=None):
        """Create a new user"""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        query = """
            INSERT INTO users (email, password_hash, first_name, last_name, phone, user_type)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        user_id = Database.execute_query(query, (email, password_hash, first_name, last_name, phone, user_type))

        # Create wallet for counsellors
        if user_type == 'counsellor':
            Database.execute_query("INSERT INTO wallets (user_id) VALUES (%s)", (user_id,))

        return user_id

    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = %s"
        return Database.execute_query(query, (email,), fetch_one=True)

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = %s"
        return Database.execute_query(query, (user_id,), fetch_one=True)

    @staticmethod
    def verify_password(stored_hash, password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

    @staticmethod
    def update_profile(user_id, **kwargs):
        """Update user profile"""
        fields = []
        values = []

        for key, value in kwargs.items():
            if key in ['first_name', 'last_name', 'phone', 'profile_image']:
                fields.append(f"{key} = %s")
                values.append(value)

        if not fields:
            return False

        values.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        Database.execute_query(query, tuple(values))
        return True


class CounsellorProfile:
    @staticmethod
    def create(user_id, license_number, specializations, bio, years_of_experience,
               hourly_rate, education=None, certifications=None, languages=None):
        """Create counsellor profile"""
        query = """
            INSERT INTO counsellor_profiles
            (user_id, license_number, specializations, bio, years_of_experience,
             hourly_rate, education, certifications, languages)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        specializations_json = json.dumps(specializations) if isinstance(specializations, list) else specializations
        education_json = json.dumps(education) if education and isinstance(education, list) else education
        certifications_json = json.dumps(certifications) if certifications and isinstance(certifications, list) else certifications
        languages_json = json.dumps(languages) if languages and isinstance(languages, list) else languages

        return Database.execute_query(query, (
            user_id, license_number, specializations_json, bio, years_of_experience,
            hourly_rate, education_json, certifications_json, languages_json
        ))

    @staticmethod
    def get_by_user_id(user_id):
        """Get counsellor profile by user ID"""
        query = """
            SELECT cp.*, u.first_name, u.last_name, u.email, u.phone, u.profile_image
            FROM counsellor_profiles cp
            JOIN users u ON cp.user_id = u.id
            WHERE cp.user_id = %s
        """
        return Database.execute_query(query, (user_id,), fetch_one=True)

    @staticmethod
    def get_by_id(counsellor_id):
        """Get counsellor profile by ID"""
        query = """
            SELECT cp.*, u.first_name, u.last_name, u.email, u.phone, u.profile_image
            FROM counsellor_profiles cp
            JOIN users u ON cp.user_id = u.id
            WHERE cp.id = %s
        """
        return Database.execute_query(query, (counsellor_id,), fetch_one=True)

    @staticmethod
    def search(specialization=None, min_rating=None, max_rate=None, city=None,
               is_available=None, page=1, page_size=20):
        """Search counsellors with filters"""
        query = """
            SELECT cp.*, u.first_name, u.last_name, u.profile_image,
                   (SELECT COUNT(*) FROM reviews WHERE counsellor_id = cp.id) as review_count
            FROM counsellor_profiles cp
            JOIN users u ON cp.user_id = u.id
            WHERE u.is_active = TRUE AND cp.verification_status = 'verified'
        """
        params = []

        if specialization:
            query += " AND cp.specializations LIKE %s"
            params.append(f'%{specialization}%')

        if min_rating:
            query += " AND cp.rating >= %s"
            params.append(min_rating)

        if max_rate:
            query += " AND cp.hourly_rate <= %s"
            params.append(max_rate)

        if city:
            query += " AND cp.city = %s"
            params.append(city)

        if is_available is not None:
            query += " AND cp.is_available = %s"
            params.append(is_available)

        query += " ORDER BY cp.rating DESC, cp.total_reviews DESC"
        query += " LIMIT %s OFFSET %s"
        params.extend([page_size, (page - 1) * page_size])

        return Database.execute_query(query, tuple(params), fetch=True)

    @staticmethod
    def update_profile(counsellor_id, **kwargs):
        """Update counsellor profile"""
        fields = []
        values = []

        allowed_fields = ['bio', 'specializations', 'hourly_rate', 'years_of_experience',
                         'education', 'certifications', 'languages', 'session_duration',
                         'video_consultation', 'audio_consultation', 'chat_consultation',
                         'address', 'city', 'state', 'country', 'zip_code',
                         'latitude', 'longitude', 'is_available']

        for key, value in kwargs.items():
            if key in allowed_fields:
                if key in ['specializations', 'education', 'certifications', 'languages']:
                    value = json.dumps(value) if isinstance(value, list) else value
                fields.append(f"{key} = %s")
                values.append(value)

        if not fields:
            return False

        values.append(counsellor_id)
        query = f"UPDATE counsellor_profiles SET {', '.join(fields)} WHERE id = %s"
        Database.execute_query(query, tuple(values))
        return True

    @staticmethod
    def update_rating(counsellor_id):
        """Recalculate counsellor rating"""
        query = """
            UPDATE counsellor_profiles
            SET rating = (
                SELECT COALESCE(AVG(rating), 0)
                FROM reviews
                WHERE counsellor_id = %s AND is_visible = TRUE
            ),
            total_reviews = (
                SELECT COUNT(*)
                FROM reviews
                WHERE counsellor_id = %s AND is_visible = TRUE
            )
            WHERE id = %s
        """
        Database.execute_query(query, (counsellor_id, counsellor_id, counsellor_id))


class Booking:
    @staticmethod
    def create(patient_id, counsellor_id, session_date, session_time, duration,
               session_type, booking_amount, platform_fee, counsellor_payout, patient_notes=None):
        """Create a new booking"""
        query = """
            INSERT INTO bookings
            (patient_id, counsellor_id, session_date, session_time, duration,
             session_type, booking_amount, platform_fee, counsellor_payout,
             patient_notes, status, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', 'pending')
        """
        return Database.execute_query(query, (
            patient_id, counsellor_id, session_date, session_time, duration,
            session_type, booking_amount, platform_fee, counsellor_payout, patient_notes
        ))

    @staticmethod
    def get_by_id(booking_id):
        """Get booking by ID"""
        query = """
            SELECT b.*,
                   u1.first_name as patient_first_name, u1.last_name as patient_last_name,
                   u1.email as patient_email, u1.phone as patient_phone,
                   u2.first_name as counsellor_first_name, u2.last_name as counsellor_last_name,
                   u2.email as counsellor_email, u2.phone as counsellor_phone,
                   cp.hourly_rate, cp.session_duration
            FROM bookings b
            JOIN users u1 ON b.patient_id = u1.id
            JOIN counsellor_profiles cp ON b.counsellor_id = cp.id
            JOIN users u2 ON cp.user_id = u2.id
            WHERE b.id = %s
        """
        return Database.execute_query(query, (booking_id,), fetch_one=True)

    @staticmethod
    def get_patient_bookings(patient_id, status=None):
        """Get all bookings for a patient"""
        query = """
            SELECT b.*,
                   u.first_name as counsellor_first_name, u.last_name as counsellor_last_name,
                   u.profile_image as counsellor_image,
                   cp.specializations, cp.rating
            FROM bookings b
            JOIN counsellor_profiles cp ON b.counsellor_id = cp.id
            JOIN users u ON cp.user_id = u.id
            WHERE b.patient_id = %s
        """
        params = [patient_id]

        if status:
            query += " AND b.status = %s"
            params.append(status)

        query += " ORDER BY b.session_date DESC, b.session_time DESC"
        return Database.execute_query(query, tuple(params), fetch=True)

    @staticmethod
    def get_counsellor_bookings(counsellor_id, status=None):
        """Get all bookings for a counsellor"""
        query = """
            SELECT b.*,
                   u.first_name as patient_first_name, u.last_name as patient_last_name,
                   u.profile_image as patient_image, u.phone as patient_phone
            FROM bookings b
            JOIN users u ON b.patient_id = u.id
            WHERE b.counsellor_id = %s
        """
        params = [counsellor_id]

        if status:
            query += " AND b.status = %s"
            params.append(status)

        query += " ORDER BY b.session_date DESC, b.session_time DESC"
        return Database.execute_query(query, tuple(params), fetch=True)

    @staticmethod
    def update_status(booking_id, status, user_id=None, notes=None):
        """Update booking status"""
        if status == 'cancelled':
            query = """
                UPDATE bookings
                SET status = %s, cancelled_by = %s, cancelled_at = NOW(), cancellation_reason = %s
                WHERE id = %s
            """
            Database.execute_query(query, (status, user_id, notes, booking_id))
        else:
            query = "UPDATE bookings SET status = %s WHERE id = %s"
            Database.execute_query(query, (status, booking_id))

        # Auto-generate session link when booking is confirmed
        if status == 'confirmed':
            # Get booking details
            booking = Booking.get_by_id(booking_id)

            # Only generate for video/audio sessions that don't have a link yet
            if booking and booking['session_type'] in ['video', 'audio'] and not booking['session_link']:
                import secrets

                # Create a secure room name
                room_token = secrets.token_urlsafe(16)
                room_name = f"session-{booking_id}-{room_token}"

                # Using Jitsi Meet
                session_link = f"https://meet.jit.si/{room_name}"

                # Update booking with session link
                Database.execute_query(
                    "UPDATE bookings SET session_link = %s WHERE id = %s",
                    (session_link, booking_id)
                )

    @staticmethod
    def check_availability(counsellor_id, session_date, session_time, duration):
        """Check if counsellor is available at given time"""
        query = """
            SELECT COUNT(*) as count FROM bookings
            WHERE counsellor_id = %s
            AND session_date = %s
            AND status NOT IN ('cancelled', 'no-show')
            AND (
                (session_time <= %s AND ADDTIME(session_time, SEC_TO_TIME(duration * 60)) > %s)
                OR
                (session_time < ADDTIME(%s, SEC_TO_TIME(%s * 60)) AND session_time >= %s)
            )
        """
        result = Database.execute_query(query, (
            counsellor_id, session_date, session_time, session_time,
            session_time, duration, session_time
        ), fetch_one=True)
        return result['count'] == 0


class Payment:
    @staticmethod
    def create(booking_id, patient_id, counsellor_id, amount, platform_fee,
               counsellor_payout, payment_method, transaction_id=None):
        """Create a payment record"""
        query = """
            INSERT INTO payments
            (booking_id, patient_id, counsellor_id, amount, platform_fee,
             counsellor_payout, payment_method, transaction_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        """
        return Database.execute_query(query, (
            booking_id, patient_id, counsellor_id, amount, platform_fee,
            counsellor_payout, payment_method, transaction_id
        ))

    @staticmethod
    def update_status(payment_id, status, transaction_id=None):
        """Update payment status"""
        if transaction_id:
            query = """
                UPDATE payments
                SET status = %s, transaction_id = %s, payment_date = NOW()
                WHERE id = %s
            """
            Database.execute_query(query, (status, transaction_id, payment_id))
        else:
            query = """
                UPDATE payments
                SET status = %s, payment_date = NOW()
                WHERE id = %s
            """
            Database.execute_query(query, (status, payment_id))

        # Update booking payment status
        if status == 'completed':
            Database.execute_query(
                "UPDATE bookings SET payment_status = 'paid' WHERE id = (SELECT booking_id FROM payments WHERE id = %s)",
                (payment_id,)
            )

            # Update counsellor wallet
            payment = Database.execute_query("SELECT * FROM payments WHERE id = %s", (payment_id,), fetch_one=True)
            if payment:
                Database.execute_query(
                    "UPDATE wallets SET balance = balance + %s, total_earned = total_earned + %s WHERE user_id = (SELECT user_id FROM counsellor_profiles WHERE id = %s)",
                    (payment['counsellor_payout'], payment['counsellor_payout'], payment['counsellor_id'])
                )

    @staticmethod
    def get_by_booking_id(booking_id):
        """Get payment by booking ID"""
        query = "SELECT * FROM payments WHERE booking_id = %s"
        return Database.execute_query(query, (booking_id,), fetch_one=True)


class Review:
    @staticmethod
    def create(booking_id, patient_id, counsellor_id, rating, review_text=None, is_anonymous=False):
        """Create a review"""
        query = """
            INSERT INTO reviews (booking_id, patient_id, counsellor_id, rating, review_text, is_anonymous)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        review_id = Database.execute_query(query, (
            booking_id, patient_id, counsellor_id, rating, review_text, is_anonymous
        ))

        # Update counsellor rating
        CounsellorProfile.update_rating(counsellor_id)

        # Update total sessions
        Database.execute_query(
            "UPDATE counsellor_profiles SET total_sessions = total_sessions + 1 WHERE id = %s",
            (counsellor_id,)
        )

        return review_id

    @staticmethod
    def get_counsellor_reviews(counsellor_id, page=1, page_size=10):
        """Get reviews for a counsellor"""
        query = """
            SELECT r.*, u.first_name, u.last_name, u.profile_image
            FROM reviews r
            LEFT JOIN users u ON r.patient_id = u.id
            WHERE r.counsellor_id = %s AND r.is_visible = TRUE
            ORDER BY r.created_at DESC
            LIMIT %s OFFSET %s
        """
        return Database.execute_query(query, (counsellor_id, page_size, (page - 1) * page_size), fetch=True)

    @staticmethod
    def add_response(review_id, counsellor_response):
        """Add counsellor response to review"""
        query = "UPDATE reviews SET counsellor_response = %s, response_date = NOW() WHERE id = %s"
        Database.execute_query(query, (counsellor_response, review_id))


class Notification:
    @staticmethod
    def create(user_id, title, message, notification_type, related_id=None):
        """Create a notification"""
        query = """
            INSERT INTO notifications (user_id, title, message, type, related_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        return Database.execute_query(query, (user_id, title, message, notification_type, related_id))

    @staticmethod
    def get_user_notifications(user_id, unread_only=False):
        """Get user notifications"""
        query = "SELECT * FROM notifications WHERE user_id = %s"
        params = [user_id]

        if unread_only:
            query += " AND is_read = FALSE"

        query += " ORDER BY created_at DESC LIMIT 50"
        return Database.execute_query(query, tuple(params), fetch=True)

    @staticmethod
    def mark_as_read(notification_id):
        """Mark notification as read"""
        query = "UPDATE notifications SET is_read = TRUE WHERE id = %s"
        Database.execute_query(query, (notification_id,))
