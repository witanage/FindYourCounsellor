from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, date, time
import json
from decimal import Decimal

from backend.config import Config
from backend.models import User, CounsellorProfile, Booking, Payment, Review, Notification

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES
app.config['SECRET_KEY'] = Config.SECRET_KEY

CORS(app)
jwt = JWTManager(app)

# Custom JSON encoder for Decimal and datetime
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'user_type']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if user already exists
        existing_user = User.get_by_email(data['email'])
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409

        # Create user
        user_id = User.create(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            user_type=data['user_type'],
            phone=data.get('phone')
        )

        # If counsellor, create profile
        if data['user_type'] == 'counsellor' and 'counsellor_profile' in data:
            profile_data = data['counsellor_profile']
            CounsellorProfile.create(
                user_id=user_id,
                license_number=profile_data.get('license_number'),
                specializations=profile_data.get('specializations', []),
                bio=profile_data.get('bio', ''),
                years_of_experience=profile_data.get('years_of_experience', 0),
                hourly_rate=profile_data.get('hourly_rate', 0),
                education=profile_data.get('education'),
                certifications=profile_data.get('certifications'),
                languages=profile_data.get('languages')
            )

        # Create access token
        access_token = create_access_token(identity=user_id)

        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'access_token': access_token
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400

        user = User.get_by_email(data['email'])
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        if not User.verify_password(user['password_hash'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        if not user['is_active']:
            return jsonify({'error': 'Account is deactivated'}), 403

        # Create access token
        access_token = create_access_token(identity=user['id'])

        # Get additional profile info for counsellors
        counsellor_profile = None
        if user['user_type'] == 'counsellor':
            counsellor_profile = CounsellorProfile.get_by_user_id(user['id'])

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'user_type': user['user_type'],
                'profile_image': user['profile_image'],
                'counsellor_profile_id': counsellor_profile['id'] if counsellor_profile else None
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        response_data = {
            'id': user['id'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'phone': user['phone'],
            'user_type': user['user_type'],
            'profile_image': user['profile_image']
        }

        # Add counsellor profile if applicable
        if user['user_type'] == 'counsellor':
            counsellor_profile = CounsellorProfile.get_by_user_id(user_id)
            if counsellor_profile:
                response_data['counsellor_profile'] = counsellor_profile

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== COUNSELLOR ENDPOINTS ====================

@app.route('/api/counsellors/search', methods=['GET'])
def search_counsellors():
    """Search counsellors with filters"""
    try:
        specialization = request.args.get('specialization')
        min_rating = request.args.get('min_rating', type=float)
        max_rate = request.args.get('max_rate', type=float)
        city = request.args.get('city')
        is_available = request.args.get('is_available', type=bool)
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), Config.MAX_PAGE_SIZE)

        counsellors = CounsellorProfile.search(
            specialization=specialization,
            min_rating=min_rating,
            max_rate=max_rate,
            city=city,
            is_available=is_available,
            page=page,
            page_size=page_size
        )

        return jsonify({
            'counsellors': counsellors,
            'page': page,
            'page_size': page_size
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/counsellors/<int:counsellor_id>', methods=['GET'])
def get_counsellor(counsellor_id):
    """Get counsellor profile by ID"""
    try:
        counsellor = CounsellorProfile.get_by_id(counsellor_id)
        if not counsellor:
            return jsonify({'error': 'Counsellor not found'}), 404

        # Get reviews
        reviews = Review.get_counsellor_reviews(counsellor_id, page=1, page_size=5)

        return jsonify({
            'counsellor': counsellor,
            'reviews': reviews
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/counsellors/<int:counsellor_id>/reviews', methods=['GET'])
def get_counsellor_reviews(counsellor_id):
    """Get all reviews for a counsellor"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 10, type=int), Config.MAX_PAGE_SIZE)

        reviews = Review.get_counsellor_reviews(counsellor_id, page, page_size)

        return jsonify({
            'reviews': reviews,
            'page': page,
            'page_size': page_size
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/counsellors/profile', methods=['PUT'])
@jwt_required()
def update_counsellor_profile():
    """Update counsellor profile"""
    try:
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)

        if user['user_type'] != 'counsellor':
            return jsonify({'error': 'Only counsellors can update counsellor profiles'}), 403

        counsellor_profile = CounsellorProfile.get_by_user_id(user_id)
        if not counsellor_profile:
            return jsonify({'error': 'Counsellor profile not found'}), 404

        data = request.get_json()
        CounsellorProfile.update_profile(counsellor_profile['id'], **data)

        return jsonify({'message': 'Profile updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== BOOKING ENDPOINTS ====================

@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    """Create a new booking"""
    try:
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)

        if user['user_type'] != 'patient':
            return jsonify({'error': 'Only patients can create bookings'}), 403

        data = request.get_json()

        # Validate required fields
        required_fields = ['counsellor_id', 'session_date', 'session_time', 'duration', 'session_type']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Get counsellor profile
        counsellor = CounsellorProfile.get_by_id(data['counsellor_id'])
        if not counsellor:
            return jsonify({'error': 'Counsellor not found'}), 404

        # Check availability
        is_available = Booking.check_availability(
            data['counsellor_id'],
            data['session_date'],
            data['session_time'],
            data['duration']
        )

        if not is_available:
            return jsonify({'error': 'Counsellor is not available at this time'}), 409

        # Calculate pricing
        booking_amount = float(counsellor['hourly_rate']) * (data['duration'] / 60)
        platform_fee = booking_amount * (Config.PLATFORM_FEE_PERCENTAGE / 100)
        counsellor_payout = booking_amount - platform_fee

        # Create booking
        booking_id = Booking.create(
            patient_id=user_id,
            counsellor_id=data['counsellor_id'],
            session_date=data['session_date'],
            session_time=data['session_time'],
            duration=data['duration'],
            session_type=data['session_type'],
            booking_amount=booking_amount,
            platform_fee=platform_fee,
            counsellor_payout=counsellor_payout,
            patient_notes=data.get('patient_notes')
        )

        # Create notification for counsellor
        Notification.create(
            user_id=counsellor['user_id'],
            title='New Booking Request',
            message=f"You have a new booking request from {user['first_name']} {user['last_name']}",
            notification_type='booking',
            related_id=booking_id
        )

        return jsonify({
            'message': 'Booking created successfully',
            'booking_id': booking_id,
            'booking_amount': booking_amount
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/bookings/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """Get booking details"""
    try:
        user_id = get_jwt_identity()
        booking = Booking.get_by_id(booking_id)

        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        # Check authorization
        user = User.get_by_id(user_id)
        counsellor_profile = CounsellorProfile.get_by_user_id(user_id) if user['user_type'] == 'counsellor' else None

        if booking['patient_id'] != user_id and (not counsellor_profile or booking['counsellor_id'] != counsellor_profile['id']):
            return jsonify({'error': 'Unauthorized'}), 403

        return jsonify({'booking': booking}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/bookings/my-bookings', methods=['GET'])
@jwt_required()
def get_my_bookings():
    """Get current user's bookings"""
    try:
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        status = request.args.get('status')

        if user['user_type'] == 'patient':
            bookings = Booking.get_patient_bookings(user_id, status)
        elif user['user_type'] == 'counsellor':
            counsellor_profile = CounsellorProfile.get_by_user_id(user_id)
            if not counsellor_profile:
                return jsonify({'error': 'Counsellor profile not found'}), 404
            bookings = Booking.get_counsellor_bookings(counsellor_profile['id'], status)
        else:
            return jsonify({'error': 'Invalid user type'}), 403

        return jsonify({'bookings': bookings}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/bookings/<int:booking_id>/status', methods=['PUT'])
@jwt_required()
def update_booking_status(booking_id):
    """Update booking status"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400

        booking = Booking.get_by_id(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        # Verify authorization
        user = User.get_by_id(user_id)
        counsellor_profile = CounsellorProfile.get_by_user_id(user_id) if user['user_type'] == 'counsellor' else None

        if booking['patient_id'] != user_id and (not counsellor_profile or booking['counsellor_id'] != counsellor_profile['id']):
            return jsonify({'error': 'Unauthorized'}), 403

        # Update status
        Booking.update_status(
            booking_id,
            data['status'],
            user_id,
            data.get('cancellation_reason')
        )

        # Create notifications
        if data['status'] == 'confirmed' and counsellor_profile:
            Notification.create(
                user_id=booking['patient_id'],
                title='Booking Confirmed',
                message=f"Your booking with {booking['counsellor_first_name']} {booking['counsellor_last_name']} has been confirmed",
                notification_type='booking',
                related_id=booking_id
            )
        elif data['status'] == 'cancelled':
            other_user_id = booking['patient_id'] if counsellor_profile else counsellor_profile['user_id'] if counsellor_profile else None
            if other_user_id:
                Notification.create(
                    user_id=other_user_id,
                    title='Booking Cancelled',
                    message=f"A booking has been cancelled",
                    notification_type='booking',
                    related_id=booking_id
                )

        return jsonify({'message': 'Booking status updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== VIDEO SESSION ENDPOINTS ====================

@app.route('/api/sessions/<int:booking_id>/room', methods=['POST'])
@jwt_required()
def create_session_room(booking_id):
    """Generate video session room for a booking"""
    try:
        user_id = get_jwt_identity()
        booking = Booking.get_by_id(booking_id)

        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        # Verify authorization (both patient and counsellor can access)
        user = User.get_by_id(user_id)
        counsellor_profile = CounsellorProfile.get_by_user_id(user_id) if user['user_type'] == 'counsellor' else None

        if booking['patient_id'] != user_id and (not counsellor_profile or booking['counsellor_id'] != counsellor_profile['id']):
            return jsonify({'error': 'Unauthorized'}), 403

        # Check if session type supports video/audio
        if booking['session_type'] not in ['video', 'audio']:
            return jsonify({'error': 'This booking is not for video/audio session'}), 400

        # Generate session link if not already exists
        if not booking['session_link']:
            import hashlib
            import secrets

            # Create a secure room name
            room_token = secrets.token_urlsafe(16)
            room_name = f"session-{booking_id}-{room_token}"

            # Using Jitsi Meet
            session_link = f"https://meet.jit.si/{room_name}"

            # Update booking with session link
            from backend.database import Database
            Database.execute_query(
                "UPDATE bookings SET session_link = %s WHERE id = %s",
                (session_link, booking_id)
            )

            booking['session_link'] = session_link

        return jsonify({
            'session_link': booking['session_link'],
            'booking_id': booking_id,
            'session_type': booking['session_type']
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sessions/<int:booking_id>/join', methods=['GET'])
@jwt_required()
def get_session_details(booking_id):
    """Get session details for joining"""
    try:
        user_id = get_jwt_identity()
        booking = Booking.get_by_id(booking_id)

        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        # Verify authorization
        user = User.get_by_id(user_id)
        counsellor_profile = CounsellorProfile.get_by_user_id(user_id) if user['user_type'] == 'counsellor' else None

        if booking['patient_id'] != user_id and (not counsellor_profile or booking['counsellor_id'] != counsellor_profile['id']):
            return jsonify({'error': 'Unauthorized'}), 403

        # Check if booking is confirmed
        if booking['status'] not in ['confirmed', 'in-progress']:
            return jsonify({'error': 'Booking must be confirmed to join session'}), 400

        # Check if session type supports video/audio
        if booking['session_type'] not in ['video', 'audio']:
            return jsonify({'error': 'This booking is not for video/audio session'}), 400

        # Ensure session link exists
        if not booking['session_link']:
            return jsonify({'error': 'Session link not generated. Please create session room first.'}), 400

        # Get participant details
        patient = User.get_by_id(booking['patient_id'])
        counsellor_user = User.get_by_id(booking['counsellor_user_id']) if 'counsellor_user_id' in booking else None

        participant_name = f"{user['first_name']} {user['last_name']}"
        participant_role = 'counsellor' if counsellor_profile else 'patient'

        return jsonify({
            'session_link': booking['session_link'],
            'booking_id': booking_id,
            'session_type': booking['session_type'],
            'session_date': booking['session_date'],
            'session_time': booking['session_time'],
            'duration': booking['duration'],
            'participant_name': participant_name,
            'participant_role': participant_role,
            'patient_name': f"{patient['first_name']} {patient['last_name']}",
            'counsellor_name': f"{booking['counsellor_first_name']} {booking['counsellor_last_name']}"
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sessions/<int:booking_id>/start', methods=['PUT'])
@jwt_required()
def start_session(booking_id):
    """Mark session as started"""
    try:
        user_id = get_jwt_identity()
        booking = Booking.get_by_id(booking_id)

        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        # Verify authorization
        user = User.get_by_id(user_id)
        counsellor_profile = CounsellorProfile.get_by_user_id(user_id) if user['user_type'] == 'counsellor' else None

        if booking['patient_id'] != user_id and (not counsellor_profile or booking['counsellor_id'] != counsellor_profile['id']):
            return jsonify({'error': 'Unauthorized'}), 403

        # Update booking status to in-progress
        if booking['status'] == 'confirmed':
            Booking.update_status(booking_id, 'in-progress')

            # Notify the other participant
            other_user_id = booking['patient_id'] if counsellor_profile else booking['counsellor_user_id']
            if other_user_id:
                Notification.create(
                    user_id=other_user_id,
                    title='Session Started',
                    message=f"Your session has started",
                    notification_type='booking',
                    related_id=booking_id
                )

        return jsonify({'message': 'Session started successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sessions/<int:booking_id>/end', methods=['PUT'])
@jwt_required()
def end_session(booking_id):
    """Mark session as completed"""
    try:
        user_id = get_jwt_identity()
        booking = Booking.get_by_id(booking_id)

        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        # Verify authorization (typically counsellor ends the session)
        user = User.get_by_id(user_id)
        counsellor_profile = CounsellorProfile.get_by_user_id(user_id) if user['user_type'] == 'counsellor' else None

        if booking['patient_id'] != user_id and (not counsellor_profile or booking['counsellor_id'] != counsellor_profile['id']):
            return jsonify({'error': 'Unauthorized'}), 403

        # Update booking status to completed
        if booking['status'] == 'in-progress':
            Booking.update_status(booking_id, 'completed')

            # Notify patient that session is complete
            Notification.create(
                user_id=booking['patient_id'],
                title='Session Completed',
                message=f"Your session with {booking['counsellor_first_name']} {booking['counsellor_last_name']} has been completed. Please leave a review!",
                notification_type='booking',
                related_id=booking_id
            )

        return jsonify({'message': 'Session ended successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== PAYMENT ENDPOINTS ====================

@app.route('/api/payments/create', methods=['POST'])
@jwt_required()
def create_payment():
    """Create payment for a booking"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if 'booking_id' not in data or 'payment_method' not in data:
            return jsonify({'error': 'Booking ID and payment method required'}), 400

        booking = Booking.get_by_id(data['booking_id'])
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        if booking['patient_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        if booking['payment_status'] == 'paid':
            return jsonify({'error': 'Booking already paid'}), 409

        # Create payment record
        payment_id = Payment.create(
            booking_id=booking['id'],
            patient_id=booking['patient_id'],
            counsellor_id=booking['counsellor_id'],
            amount=booking['booking_amount'],
            platform_fee=booking['platform_fee'],
            counsellor_payout=booking['counsellor_payout'],
            payment_method=data['payment_method'],
            transaction_id=data.get('transaction_id')
        )

        # In real implementation, integrate with Stripe/PayPal here
        # For now, we'll mark it as completed
        Payment.update_status(payment_id, 'completed', data.get('transaction_id', f'TXN{payment_id}'))

        # Update booking status
        Booking.update_status(booking['id'], 'confirmed')

        # Notify counsellor
        Notification.create(
            user_id=booking['counsellor_id'],
            title='Payment Received',
            message=f"Payment received for booking #{booking['id']}",
            notification_type='payment',
            related_id=booking['id']
        )

        return jsonify({
            'message': 'Payment processed successfully',
            'payment_id': payment_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/payments/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get payment details"""
    try:
        user_id = get_jwt_identity()
        payment = Payment.get_by_booking_id(payment_id)

        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        # Verify authorization
        user = User.get_by_id(user_id)
        counsellor_profile = CounsellorProfile.get_by_user_id(user_id) if user['user_type'] == 'counsellor' else None

        if payment['patient_id'] != user_id and (not counsellor_profile or payment['counsellor_id'] != counsellor_profile['id']):
            return jsonify({'error': 'Unauthorized'}), 403

        return jsonify({'payment': payment}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== REVIEW ENDPOINTS ====================

@app.route('/api/reviews', methods=['POST'])
@jwt_required()
def create_review():
    """Create a review for a completed booking"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        required_fields = ['booking_id', 'rating']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Booking ID and rating required'}), 400

        booking = Booking.get_by_id(data['booking_id'])
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        if booking['patient_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        if booking['status'] != 'completed':
            return jsonify({'error': 'Can only review completed bookings'}), 400

        # Check if review already exists
        from backend.database import Database
        existing = Database.execute_query(
            "SELECT id FROM reviews WHERE booking_id = %s",
            (data['booking_id'],),
            fetch_one=True
        )
        if existing:
            return jsonify({'error': 'Review already exists for this booking'}), 409

        # Create review
        review_id = Review.create(
            booking_id=data['booking_id'],
            patient_id=user_id,
            counsellor_id=booking['counsellor_id'],
            rating=data['rating'],
            review_text=data.get('review_text'),
            is_anonymous=data.get('is_anonymous', False)
        )

        # Notify counsellor
        Notification.create(
            user_id=booking['counsellor_id'],
            title='New Review',
            message=f"You received a new {data['rating']}-star review",
            notification_type='review',
            related_id=review_id
        )

        return jsonify({
            'message': 'Review created successfully',
            'review_id': review_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== NOTIFICATION ENDPOINTS ====================

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications"""
    try:
        user_id = get_jwt_identity()
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'

        notifications = Notification.get_user_notifications(user_id, unread_only)

        return jsonify({'notifications': notifications}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        Notification.mark_as_read(notification_id)
        return jsonify({'message': 'Notification marked as read'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== SPECIALIZATIONS ENDPOINT ====================

@app.route('/api/specializations', methods=['GET'])
def get_specializations():
    """Get all specializations"""
    try:
        from backend.database import Database
        specializations = Database.execute_query(
            "SELECT * FROM specializations WHERE is_active = TRUE ORDER BY name",
            fetch=True
        )
        return jsonify({'specializations': specializations}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Counselling Marketplace API is running'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
