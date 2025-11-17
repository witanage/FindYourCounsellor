// API Configuration
const API_URL = 'http://localhost:5005/api';

// Theme Management
function getTheme() {
    return localStorage.getItem('theme') || 'light';
}

function setTheme(theme) {
    localStorage.setItem('theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
}

function toggleTheme() {
    const currentTheme = getTheme();
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    updateThemeButton();
}

function updateThemeButton() {
    const themeButton = document.getElementById('themeToggle');
    if (themeButton) {
        const currentTheme = getTheme();
        const icon = themeButton.querySelector('.theme-toggle-icon');
        const text = themeButton.querySelector('.theme-toggle-text');

        if (currentTheme === 'dark') {
            icon.textContent = '☀️';
            text.textContent = 'Light';
        } else {
            icon.textContent = '🌙';
            text.textContent = 'Dark';
        }
    }
}

function initTheme() {
    const savedTheme = getTheme();
    setTheme(savedTheme);
    updateThemeButton();
}

// Utility Functions
function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(token) {
    localStorage.setItem('access_token', token);
}

function removeToken() {
    localStorage.removeItem('access_token');
}

function getCurrentUser() {
    const user = localStorage.getItem('current_user');
    return user ? JSON.parse(user) : null;
}

function setCurrentUser(user) {
    localStorage.setItem('current_user', JSON.stringify(user));
}

function removeCurrentUser() {
    localStorage.removeItem('current_user');
}

function isAuthenticated() {
    return !!getToken();
}

function logout() {
    removeToken();
    removeCurrentUser();
    window.location.href = 'login.html';
}

// API Request Helper
async function apiRequest(endpoint, options = {}) {
    const url = `${API_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (getToken()) {
        headers['Authorization'] = `Bearer ${getToken()}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        const data = await response.json();

        if (!response.ok) {
            const error = new Error(data.error || 'Request failed');
            error.status = response.status;
            throw error;
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Notification System
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Format Date/Time
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatTime(timeString) {
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
}

function formatCurrency(amount) {
    return `$${parseFloat(amount).toFixed(2)}`;
}

// Star Rating Display
function getStarRating(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5 ? 1 : 0;
    const emptyStars = 5 - fullStars - halfStar;

    let stars = '';
    for (let i = 0; i < fullStars; i++) stars += '★';
    if (halfStar) stars += '☆';
    for (let i = 0; i < emptyStars; i++) stars += '☆';

    return stars;
}

// Modal Helper
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Initialize Auth Check
function initAuthCheck() {
    const publicPages = ['index.html', 'login.html', 'register.html', ''];
    const currentPage = window.location.pathname.split('/').pop();

    if (!isAuthenticated() && !publicPages.includes(currentPage)) {
        window.location.href = 'login.html';
    }
}

// Navigation Menu Update
function updateNavigation() {
    const user = getCurrentUser();
    const navMenu = document.querySelector('.navbar-menu');

    if (navMenu && user) {
        const authLinks = navMenu.querySelectorAll('.auth-link');
        authLinks.forEach(link => link.remove());

        const userType = user.user_type;
        let dashboardLink = '';

        if (userType === 'patient') {
            dashboardLink = '<li><a href="patient-dashboard.html" class="auth-link">Dashboard</a></li>';
        } else if (userType === 'counsellor') {
            dashboardLink = '<li><a href="counsellor-dashboard.html" class="auth-link">Dashboard</a></li>';
        } else if (userType === 'admin') {
            dashboardLink = '<li><a href="admin-dashboard.html" class="auth-link">Admin</a></li>';
        }

        navMenu.innerHTML += dashboardLink;
        navMenu.innerHTML += '<li><a href="#" onclick="logout()" class="auth-link">Logout</a></li>';
    }

    // Add theme toggle button if not exists
    addThemeToggleButton();
}

// Add theme toggle button to navbar
function addThemeToggleButton() {
    const navMenu = document.querySelector('.navbar-menu');
    if (navMenu && !document.getElementById('themeToggle')) {
        const themeToggleItem = document.createElement('li');
        const currentTheme = getTheme();
        const icon = currentTheme === 'dark' ? '☀️' : '🌙';
        const text = currentTheme === 'dark' ? 'Light' : 'Dark';

        themeToggleItem.innerHTML = `
            <button id="themeToggle" class="theme-toggle" onclick="toggleTheme()">
                <span class="theme-toggle-icon">${icon}</span>
                <span class="theme-toggle-text">${text}</span>
            </button>
        `;
        navMenu.appendChild(themeToggleItem);
    }
}

// Load User Profile
async function loadUserProfile() {
    try {
        const data = await apiRequest('/auth/me');
        setCurrentUser(data);
        return data;
    } catch (error) {
        console.error('Failed to load user profile:', error);
        // Only logout if it's an authentication error (401 or 403)
        // For other errors (network issues, server errors), don't force logout
        if (error.status === 401 || error.status === 403) {
            console.error('Authentication failed, logging out');
            logout();
        } else {
            // For other errors, just throw so the caller can handle it
            throw error;
        }
    }
}

// Search Counsellors
async function searchCounsellors(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return await apiRequest(`/counsellors/search?${queryParams}`);
}

// Create Booking
async function createBooking(bookingData) {
    return await apiRequest('/bookings', {
        method: 'POST',
        body: JSON.stringify(bookingData)
    });
}

// Process Payment
async function processPayment(paymentData) {
    return await apiRequest('/payments/create', {
        method: 'POST',
        body: JSON.stringify(paymentData)
    });
}

// Create Review
async function createReview(reviewData) {
    return await apiRequest('/reviews', {
        method: 'POST',
        body: JSON.stringify(reviewData)
    });
}

// Get My Bookings
async function getMyBookings(status = null) {
    const query = status ? `?status=${status}` : '';
    return await apiRequest(`/bookings/my-bookings${query}`);
}

// Update Booking Status
async function updateBookingStatus(bookingId, status, reason = null) {
    return await apiRequest(`/bookings/${bookingId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status, cancellation_reason: reason })
    });
}

// Get Notifications
async function getNotifications(unreadOnly = false) {
    const query = unreadOnly ? '?unread_only=true' : '';
    return await apiRequest(`/notifications${query}`);
}

// Mark Notification as Read
async function markNotificationRead(notificationId) {
    return await apiRequest(`/notifications/${notificationId}/read`, {
        method: 'PUT'
    });
}

// Video Session API
const api = {
    get: async (endpoint) => {
        return await apiRequest(endpoint, { method: 'GET' });
    },
    post: async (endpoint, data) => {
        return await apiRequest(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    put: async (endpoint, data) => {
        return await apiRequest(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme first
    initTheme();

    // Add theme toggle button to navbar
    addThemeToggleButton();

    // Check auth and update navigation
    initAuthCheck();
    if (isAuthenticated()) {
        updateNavigation();
    }
});
