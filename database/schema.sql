-- CounsellingMarketplace Database Schema
-- Drop database if exists and create new
DROP DATABASE IF EXISTS counselling_marketplace;
CREATE DATABASE counselling_marketplace;
USE counselling_marketplace;

-- Users Table (Base table for all users)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    user_type ENUM('patient', 'counsellor', 'admin') NOT NULL,
    profile_image VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_user_type (user_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Counsellor Profiles (Extended information for counsellors)
CREATE TABLE counsellor_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    license_number VARCHAR(100) UNIQUE,
    specializations TEXT, -- JSON array of specializations
    bio TEXT,
    years_of_experience INT,
    education TEXT, -- JSON array of education details
    certifications TEXT, -- JSON array of certifications
    languages TEXT, -- JSON array of languages
    hourly_rate DECIMAL(10, 2) NOT NULL,
    session_duration INT DEFAULT 60, -- in minutes
    is_available BOOLEAN DEFAULT FALSE,
    rating DECIMAL(3, 2) DEFAULT 0.00,
    total_sessions INT DEFAULT 0,
    total_reviews INT DEFAULT 0,
    video_consultation BOOLEAN DEFAULT TRUE,
    audio_consultation BOOLEAN DEFAULT TRUE,
    chat_consultation BOOLEAN DEFAULT TRUE,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    zip_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    verification_status ENUM('pending', 'verified', 'rejected') DEFAULT 'pending',
    verification_documents TEXT, -- JSON array of document URLs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_rating (rating),
    INDEX idx_hourly_rate (hourly_rate),
    INDEX idx_specializations (specializations(255)),
    INDEX idx_city (city),
    INDEX idx_verification_status (verification_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Availability Schedule (Counsellor availability)
CREATE TABLE availability_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    counsellor_id INT NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (counsellor_id) REFERENCES counsellor_profiles(id) ON DELETE CASCADE,
    INDEX idx_counsellor_day (counsellor_id, day_of_week)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Time Off / Blocked Slots
CREATE TABLE time_off (
    id INT AUTO_INCREMENT PRIMARY KEY,
    counsellor_id INT NOT NULL,
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME NOT NULL,
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (counsellor_id) REFERENCES counsellor_profiles(id) ON DELETE CASCADE,
    INDEX idx_counsellor_dates (counsellor_id, start_datetime, end_datetime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Booking/Sessions Table (Similar to Uber rides)
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    counsellor_id INT NOT NULL,
    session_date DATE NOT NULL,
    session_time TIME NOT NULL,
    duration INT NOT NULL, -- in minutes
    session_type ENUM('video', 'audio', 'chat', 'in-person') NOT NULL,
    status ENUM('pending', 'confirmed', 'in-progress', 'completed', 'cancelled', 'no-show') DEFAULT 'pending',
    booking_amount DECIMAL(10, 2) NOT NULL,
    platform_fee DECIMAL(10, 2) NOT NULL,
    counsellor_payout DECIMAL(10, 2) NOT NULL,
    payment_status ENUM('pending', 'paid', 'refunded', 'failed') DEFAULT 'pending',
    patient_notes TEXT,
    counsellor_notes TEXT,
    session_link VARCHAR(255), -- For video/audio consultations
    cancellation_reason TEXT,
    cancelled_by INT, -- user_id who cancelled
    cancelled_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id),
    FOREIGN KEY (counsellor_id) REFERENCES counsellor_profiles(id),
    FOREIGN KEY (cancelled_by) REFERENCES users(id),
    INDEX idx_patient (patient_id),
    INDEX idx_counsellor (counsellor_id),
    INDEX idx_session_datetime (session_date, session_time),
    INDEX idx_status (status),
    INDEX idx_payment_status (payment_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Payments Table
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT UNIQUE NOT NULL,
    patient_id INT NOT NULL,
    counsellor_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    platform_fee DECIMAL(10, 2) NOT NULL,
    counsellor_payout DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('card', 'paypal', 'stripe', 'wallet') NOT NULL,
    transaction_id VARCHAR(255) UNIQUE,
    stripe_payment_intent_id VARCHAR(255),
    status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    payment_date TIMESTAMP NULL,
    refund_amount DECIMAL(10, 2),
    refund_date TIMESTAMP NULL,
    refund_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (patient_id) REFERENCES users(id),
    FOREIGN KEY (counsellor_id) REFERENCES counsellor_profiles(id),
    INDEX idx_booking (booking_id),
    INDEX idx_transaction (transaction_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Reviews and Ratings
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT UNIQUE NOT NULL,
    patient_id INT NOT NULL,
    counsellor_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    is_anonymous BOOLEAN DEFAULT FALSE,
    counsellor_response TEXT,
    response_date TIMESTAMP NULL,
    is_visible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (patient_id) REFERENCES users(id),
    FOREIGN KEY (counsellor_id) REFERENCES counsellor_profiles(id),
    INDEX idx_counsellor (counsellor_id),
    INDEX idx_rating (rating),
    INDEX idx_visible (is_visible)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Specializations Master Table
CREATE TABLE specializations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Notifications Table
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('booking', 'payment', 'review', 'system', 'promotion') NOT NULL,
    related_id INT, -- ID of related booking, payment, etc.
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_read (user_id, is_read),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Wallet/Earnings Table (For counsellors)
CREATE TABLE wallets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    balance DECIMAL(10, 2) DEFAULT 0.00,
    total_earned DECIMAL(10, 2) DEFAULT 0.00,
    total_withdrawn DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Withdrawal Requests
CREATE TABLE withdrawal_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'approved', 'rejected', 'completed') DEFAULT 'pending',
    payment_method VARCHAR(100),
    payment_details TEXT, -- JSON with bank details, PayPal email, etc.
    admin_notes TEXT,
    processed_by INT,
    processed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (processed_by) REFERENCES users(id),
    INDEX idx_user_status (user_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Favorites/Saved Counsellors
CREATE TABLE favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    counsellor_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (counsellor_id) REFERENCES counsellor_profiles(id) ON DELETE CASCADE,
    UNIQUE KEY unique_favorite (patient_id, counsellor_id),
    INDEX idx_patient (patient_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Chat Messages (Optional - for chat consultations)
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    sender_id INT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    INDEX idx_booking_created (booking_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default specializations
INSERT INTO specializations (name, description, icon) VALUES
('Anxiety & Stress', 'Help with anxiety disorders, stress management, and panic attacks', 'anxiety-icon'),
('Depression', 'Support for depression, mood disorders, and emotional wellness', 'depression-icon'),
('Relationship Issues', 'Couples therapy, family counseling, and relationship guidance', 'relationship-icon'),
('Trauma & PTSD', 'Treatment for trauma, PTSD, and traumatic experiences', 'trauma-icon'),
('Addiction', 'Support for substance abuse and behavioral addictions', 'addiction-icon'),
('Career Counseling', 'Career guidance, workplace stress, and professional development', 'career-icon'),
('Child & Adolescent', 'Therapy for children and teenagers', 'child-icon'),
('Eating Disorders', 'Treatment for eating disorders and body image issues', 'eating-icon'),
('Grief & Loss', 'Support through bereavement and loss', 'grief-icon'),
('LGBTQ+ Issues', 'Counseling for LGBTQ+ individuals and related concerns', 'lgbtq-icon'),
('Life Transitions', 'Support during major life changes and transitions', 'transition-icon'),
('Sleep Disorders', 'Help with insomnia and sleep-related issues', 'sleep-icon');

-- Create admin user (password: admin123)
INSERT INTO users (email, password_hash, first_name, last_name, user_type, is_active, is_verified)
VALUES ('admin@counselling.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLHJ7cGu', 'Admin', 'User', 'admin', TRUE, TRUE);
