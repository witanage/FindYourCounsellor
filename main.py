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
    print("=" * 70)
    print("FindYourCounsellor - Counselling Marketplace Platform")
    print("=" * 70)
    print("\n🚀 Application Server starting...")
    print("=" * 70)
    print("\n📱 FRONTEND & BACKEND running on: http://localhost:5005")
    print("\n🌐 Access the application:")
    print("   Landing Page:        http://localhost:5005")
    print("   Login:               http://localhost:5005/login.html")
    print("   Register (Patient):  http://localhost:5005/register.html")
    print("   Search Counsellors:  http://localhost:5005/search.html")
    print("\n🔑 Admin Account:")
    print("   Email:    admin@counselling.com")
    print("   Password: admin123")
    print("\n📚 API Documentation:")
    print("   Base URL: http://localhost:5005/api")
    print("   Health:   http://localhost:5005/api/health")
    print("\n🎨 Features Available:")
    print("   ✓ Video/Audio Conferencing (Jitsi Meet)")
    print("   ✓ Dark/Light Theme Toggle")
    print("   ✓ Secure JWT Authentication")
    print("   ✓ Payment Processing")
    print("   ✓ Reviews & Ratings")
    print("\n⚠️  Prerequisites:")
    print("   • MySQL must be running")
    print("   • Database must be set up:")
    print("     mysql -u root -p < database/schema.sql")
    print("   • Update .env file with your MySQL password")
    print("\n⌨️  Press CTRL+C to stop the server")
    print("=" * 70)
    print()

    app.run(debug=True, host='0.0.0.0', port=5005)
