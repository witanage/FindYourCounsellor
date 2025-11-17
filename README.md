# FindYourCounsellor - Counselling Marketplace Platform

A comprehensive counselling marketplace platform similar to Uber, connecting patients with licensed counsellors. Built with Python (Flask), MySQL, and vanilla JavaScript.

## Features

### For Patients
- 🔍 **Search & Filter** - Find counsellors by specialization, location, rating, and price
- 📅 **Easy Booking** - Book sessions with real-time availability checking
- 💳 **Secure Payments** - Integrated payment processing with Stripe
- ⭐ **Reviews & Ratings** - Read and write reviews for counsellors
- 📱 **Multiple Formats** - Video, audio, chat, or in-person consultations
- 🎥 **Video/Audio Conferencing** - Built-in Jitsi Meet integration for secure video calls
- 📊 **Dashboard** - Track all your bookings and sessions

### For Counsellors
- 👤 **Professional Profiles** - Showcase expertise, education, and certifications
- 🕐 **Availability Management** - Control your schedule and time slots
- 💰 **Earnings Tracking** - Monitor income and request withdrawals
- 📈 **Performance Metrics** - View ratings, reviews, and session statistics
- ✅ **Booking Management** - Accept/decline session requests
- 🎥 **Video Sessions** - Conduct secure video/audio sessions with Jitsi Meet
- 💬 **Client Communication** - Connect with patients through the platform

### For Administrators
- 📊 **Platform Overview** - Monitor all platform activities
- ✓ **Counsellor Verification** - Review and approve counsellor registrations
- 💸 **Payment Management** - Handle withdrawal requests
- 📈 **Analytics** - Track platform growth and revenue

## Technology Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **MySQL** - Database
- **JWT** - Authentication
- **bcrypt** - Password hashing
- **Stripe** - Payment processing (optional)

### Frontend
- **HTML5/CSS3** - Structure and styling
- **Vanilla JavaScript** - No frameworks, pure JS
- **Jitsi Meet** - Video/audio conferencing integration
- **Responsive Design** - Mobile-friendly interface

## Project Structure

```
FindYourCounsellor/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database connection handler
│   └── models.py           # Data models and business logic
├── frontend/
│   ├── css/
│   │   └── styles.css      # Application styles
│   ├── js/
│   │   └── app.js          # JavaScript utilities and API calls
│   ├── index.html          # Landing page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── search.html         # Counsellor search page
│   ├── patient-dashboard.html      # Patient dashboard
│   ├── counsellor-dashboard.html   # Counsellor dashboard
│   ├── admin-dashboard.html        # Admin dashboard
│   └── video-session.html          # Video/Audio conferencing interface
├── database/
│   └── schema.sql          # Database schema
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd FindYourCounsellor
```

### Step 2: Set Up MySQL Database
```bash
# Login to MySQL
mysql -u root -p

# Run the schema file
mysql -u root -p < database/schema.sql
```

This will:
- Create the `counselling_marketplace` database
- Create all necessary tables
- Insert default specializations
- Create an admin user (email: admin@counselling.com, password: admin123)

### Step 3: Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

Update the following variables:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=counselling_marketplace

JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
SECRET_KEY=your-super-secret-key-change-this

# Optional: Stripe keys for payment processing
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
```

### Step 4: Install Python Dependencies
```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Run the Application

#### Start the Backend Server
```bash
cd backend
python app.py
```

The backend API will run on `http://localhost:5005`

#### Serve the Frontend
You can use any static file server. Here are a few options:

**Option 1: Python HTTP Server**
```bash
cd frontend
python -m http.server 8000
```

**Option 2: Node.js http-server**
```bash
cd frontend
npx http-server -p 8000
```

**Option 3: Live Server (VS Code Extension)**
- Install the "Live Server" extension in VS Code
- Right-click on `frontend/index.html`
- Select "Open with Live Server"

The frontend will be available at `http://localhost:8000`

### Step 6: Access the Application
- **Landing Page**: http://localhost:8000
- **Patient Registration**: http://localhost:8000/register.html
- **Counsellor Registration**: http://localhost:8000/register.html?type=counsellor
- **Login**: http://localhost:8000/login.html
- **Admin Login**: Use email: `admin@counselling.com`, password: `admin123`
- **Backend API**: http://localhost:5005

## API Documentation

### Base URL
```
http://localhost:5005/api
```

### Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### API Endpoints

#### Authentication

**Register User**
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "user_type": "patient",
  "counsellor_profile": {  // Only for counsellors
    "license_number": "LIC123",
    "specializations": ["Anxiety", "Depression"],
    "bio": "Professional counsellor...",
    "years_of_experience": 5,
    "hourly_rate": 100
  }
}
```

**Login**
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Get Current User**
```http
GET /auth/me
Authorization: Bearer <token>
```

#### Counsellors

**Search Counsellors**
```http
GET /counsellors/search?specialization=Anxiety&city=NewYork&min_rating=4.0&max_rate=150&page=1
```

**Get Counsellor Details**
```http
GET /counsellors/{counsellor_id}
```

**Get Counsellor Reviews**
```http
GET /counsellors/{counsellor_id}/reviews?page=1&page_size=10
```

**Update Counsellor Profile**
```http
PUT /counsellors/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "bio": "Updated bio",
  "hourly_rate": 120,
  "is_available": true
}
```

#### Bookings

**Create Booking**
```http
POST /bookings
Authorization: Bearer <token>
Content-Type: application/json

{
  "counsellor_id": 1,
  "session_date": "2025-12-01",
  "session_time": "14:00:00",
  "duration": 60,
  "session_type": "video",
  "patient_notes": "First session"
}
```

**Get Booking Details**
```http
GET /bookings/{booking_id}
Authorization: Bearer <token>
```

**Get My Bookings**
```http
GET /bookings/my-bookings?status=confirmed
Authorization: Bearer <token>
```

**Update Booking Status**
```http
PUT /bookings/{booking_id}/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "confirmed",
  "cancellation_reason": "Optional reason if cancelling"
}
```

#### Payments

**Create Payment**
```http
POST /payments/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "booking_id": 1,
  "payment_method": "card",
  "transaction_id": "txn_123"
}
```

**Get Payment Details**
```http
GET /payments/{payment_id}
Authorization: Bearer <token>
```

#### Reviews

**Create Review**
```http
POST /reviews
Authorization: Bearer <token>
Content-Type: application/json

{
  "booking_id": 1,
  "rating": 5,
  "review_text": "Excellent session!",
  "is_anonymous": false
}
```

#### Notifications

**Get Notifications**
```http
GET /notifications?unread_only=true
Authorization: Bearer <token>
```

**Mark Notification as Read**
```http
PUT /notifications/{notification_id}/read
Authorization: Bearer <token>
```

#### Video Sessions

**Create/Get Video Session Room**
```http
POST /sessions/{booking_id}/room
Authorization: Bearer <token>
```

**Get Session Details for Joining**
```http
GET /sessions/{booking_id}/join
Authorization: Bearer <token>
```

**Start Video Session**
```http
PUT /sessions/{booking_id}/start
Authorization: Bearer <token>
```

**End Video Session**
```http
PUT /sessions/{booking_id}/end
Authorization: Bearer <token>
```

#### Specializations

**Get All Specializations**
```http
GET /specializations
```

## Video/Audio Conferencing

The platform includes built-in video and audio conferencing powered by **Jitsi Meet**.

### Features
- **Secure Video Calls** - End-to-end encrypted sessions
- **Audio-Only Mode** - For audio consultations
- **Session Timer** - Real-time duration tracking
- **Automatic Link Generation** - Secure room URLs created automatically
- **Session Management** - Start/end tracking with notifications
- **No Additional Setup** - Uses public Jitsi servers by default

### How It Works

1. **Booking Confirmation**: When a counsellor confirms a video/audio booking, a secure Jitsi Meet room is automatically created
2. **Join Session**: Both patient and counsellor can click "Join Session" button from their dashboards
3. **Full-Screen Interface**: Opens a dedicated video call page with:
   - Session information (participants, duration, type)
   - Real-time timer
   - Full Jitsi Meet controls (mic, camera, screen share, chat)
   - End session button
4. **Session Status**: Automatically updates booking status to "in-progress" when started
5. **Completion**: Either party can end the session, marking it as completed

### Self-Hosting Jitsi (Optional)

To use your own Jitsi Meet server instead of public servers:

1. Install Jitsi Meet on your server (see [Jitsi documentation](https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-quickstart))
2. Update the domain in `backend/app.py`:
   ```python
   # Line 475 in app.py
   session_link = f"https://your-jitsi-domain.com/{room_name}"
   ```
3. Update the domain in `frontend/video-session.html`:
   ```javascript
   // Line 242
   const domain = 'your-jitsi-domain.com';
   ```

## Database Schema

### Key Tables

- **users** - Base user information (patients, counsellors, admins)
- **counsellor_profiles** - Extended counsellor information
- **bookings** - Session bookings (similar to Uber rides)
- **payments** - Payment transactions
- **reviews** - Counsellor reviews and ratings
- **availability_schedules** - Counsellor availability
- **notifications** - In-app notifications
- **wallets** - Counsellor earnings tracking
- **specializations** - Counselling specializations

See `database/schema.sql` for the complete schema.

## User Workflows

### Patient Journey
1. Register/Login
2. Search for counsellors by specialization/location
3. View counsellor profiles and reviews
4. Book a session with available time slot
5. Make payment
6. Attend session (video/audio/chat)
7. Leave a review

### Counsellor Journey
1. Register with professional credentials
2. Complete profile (bio, specializations, rates)
3. Set availability schedule
4. Receive booking requests
5. Accept/decline requests
6. Conduct sessions
7. Track earnings
8. Request withdrawals

### Admin Journey
1. Login to admin dashboard
2. Review counsellor verification requests
3. Approve/reject counsellor registrations
4. Monitor platform activities
5. Process withdrawal requests
6. View analytics and reports

## Security Features

- **Password Hashing** - bcrypt for secure password storage
- **JWT Authentication** - Stateless authentication
- **SQL Injection Prevention** - Parameterized queries
- **Input Validation** - Server-side validation
- **CORS Protection** - Configured for specific origins
- **Role-Based Access Control** - User type verification

## Platform Fee Model

The platform operates on a commission-based model similar to Uber:
- **Platform Fee**: 15% of booking amount
- **Counsellor Payout**: 85% of booking amount

Example:
- Hourly Rate: $100
- 60-minute session: $100
- Platform Fee: $15
- Counsellor receives: $85

## Testing

### Test Accounts

**Admin Account**
- Email: admin@counselling.com
- Password: admin123

**Create Test Counsellor**
1. Go to registration page
2. Select "I'm a counsellor"
3. Fill in details
4. Login to counsellor dashboard

**Create Test Patient**
1. Go to registration page
2. Select "I'm looking for counselling"
3. Fill in details
4. Search and book counsellors

## Future Enhancements

- [x] Real-time video/audio calling integration (✅ Completed with Jitsi Meet)
- [ ] SMS/Email notifications
- [ ] Advanced search filters (insurance, languages, etc.)
- [ ] Automated scheduling system
- [ ] Mobile apps (iOS/Android)
- [ ] AI-powered counsellor recommendations
- [ ] Insurance integration
- [ ] Prescription management
- [ ] Group therapy sessions
- [ ] Recurring appointments

## Troubleshooting

### Database Connection Issues
```bash
# Check MySQL is running
sudo systemctl status mysql

# Verify database exists
mysql -u root -p -e "SHOW DATABASES;"

# Check user permissions
mysql -u root -p -e "SHOW GRANTS FOR 'your_user'@'localhost';"
```

### CORS Issues
If you encounter CORS errors, ensure:
1. Flask-CORS is installed
2. Backend is running on port 5005
3. Frontend is accessing the correct API URL (http://localhost:5005/api)

### JWT Token Issues
- Tokens expire after 24 hours
- Check JWT_SECRET_KEY matches in .env
- Clear localStorage and login again

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Create an issue on GitHub
- Email: support@findyourcounsellor.com

## Acknowledgments

- Built with Flask and MySQL
- Inspired by Uber's marketplace model
- Designed for mental health accessibility

---

**Made with ❤️ for better mental health access**
