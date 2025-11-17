#!/usr/bin/env python3
"""
FindYourCounsellor - Counselling Marketplace Platform
Main entry point for the application
"""

import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import app

if __name__ == '__main__':
    print("=" * 60)
    print("FindYourCounsellor - Counselling Marketplace Platform")
    print("=" * 60)
    print("\nBackend API Server starting...")
    print("API will be available at: http://localhost:5005/api")
    print("\nAvailable endpoints:")
    print("  - POST   /api/auth/register")
    print("  - POST   /api/auth/login")
    print("  - GET    /api/auth/me")
    print("  - GET    /api/counsellors/search")
    print("  - POST   /api/bookings")
    print("  - GET    /api/bookings/my-bookings")
    print("  - POST   /api/payments/create")
    print("  - POST   /api/reviews")
    print("  - GET    /api/notifications")
    print("  - GET    /api/specializations")
    print("  - POST   /api/sessions/<booking_id>/room")
    print("  - GET    /api/sessions/<booking_id>/join")
    print("  - PUT    /api/sessions/<booking_id>/start")
    print("  - PUT    /api/sessions/<booking_id>/end")
    print("  - GET    /api/health")
    print("\nAdmin Account:")
    print("  Email: admin@counselling.com")
    print("  Password: admin123")
    print("\nMake sure MySQL is running and database is set up!")
    print("Run: mysql -u root -p < database/schema.sql")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)
    print()

    app.run(debug=True, host='0.0.0.0', port=5005)
