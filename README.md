# Lykke Travel Booking System

A comprehensive Django-based travel booking platform that allows users to browse destinations, book travel packages, and manage their bookings with integrated payment processing.

## 🌟 Features

### User Management
- **User Registration & Authentication**: Secure user registration and login system
- **User Profiles**: Customizable user profiles with personal information management
- **Profile Management**: Users can edit their personal details and preferences

### Travel & Destinations
- **Destination Browse**: Explore various travel destinations with detailed information
- **Travel Options**: Multiple travel types (flights, buses, trains) with different operators
- **Dynamic Pricing**: Real-time pricing based on travel type and availability
- **Seat Management**: Real-time seat availability tracking

### Booking System
- **Multi-Passenger Booking**: Book for multiple passengers in a single transaction
- **Dynamic Forms**: Add/remove passengers dynamically with client-side validation
- **Booking Management**: View all bookings with status tracking
- **Status Management**: Track booking status (Pending, Confirmed, Cancelled)

### Payment Integration
- **Razorpay Integration**: Secure payment processing with Razorpay gateway
- **UPI Support**: Enhanced UPI payment options with prominent display
- **Payment Status Tracking**: Real-time payment status updates
- **Signature Verification**: Secure payment verification with signature validation

### User Interface
- **Responsive Design**: Mobile-first responsive design using Bootstrap 5
- **Modern UI/UX**: Clean, intuitive interface with smooth animations
- **Dynamic Content**: Real-time updates and interactive elements
- **Status Indicators**: Visual status indicators for bookings and payments

## 🛠️ Technology Stack

### Backend
- **Django 5.2.5**: Python web framework
- **MySQL**: Database management system
- **Razorpay 1.4.1**: Payment gateway integration

### Frontend
- **Bootstrap 5**: CSS framework for responsive design
- **JavaScript**: Dynamic form handling and user interactions
- **FontAwesome**: Icon library for enhanced UI

### Development Tools
- **Python 3.13**: Programming language
- **Virtual Environment**: Isolated Python environment
- **Git**: Version control system

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.11 or higher
- MySQL Server
- Git
- Virtual environment (venv)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Parvm1102/lykke.git
cd lykke
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE lykke_db;
EXIT;

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Environment Configuration
Create a `.env` file in the project root:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_NAME=lykke_db
DATABASE_USER=your-mysql-username
DATABASE_PASSWORD=your-mysql-password
DATABASE_HOST=localhost
DATABASE_PORT=3306
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
```

### 7. Load Sample Data (Optional)
```bash
python manage.py loaddata fixtures/destinations.json
python manage.py loaddata fixtures/travel_options.json
```

### 8. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 📁 Project Structure

```
lykke/
├── core/                       # Main application
│   ├── models.py              # Database models
│   ├── views.py               # View controllers
│   ├── forms.py               # Form definitions
│   ├── urls.py                # URL routing
│   ├── admin.py               # Admin configuration
│   ├── migrations/            # Database migrations
│   ├── templates/core/        # HTML templates
│   │   ├── base.html         # Base template
│   │   ├── home.html         # Homepage
│   │   ├── booking.html      # Booking form
│   │   ├── payment.html      # Payment page
│   │   ├── my_bookings.html  # User bookings
│   │   └── ...
│   ├── static/core/          # Static files
│   │   ├── css/             # Stylesheets
│   │   ├── js/              # JavaScript files
│   │   └── images/          # Images
│   └── ...
├── lykke/                     # Project settings
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL configuration
│   ├── wsgi.py               # WSGI configuration
│   └── ...
├── static/                    # Collected static files
├── media/                     # User uploaded files
├── requirements.txt           # Python dependencies
├── manage.py                 # Django management script
└── README.md                 # This file
```

## 🔧 Configuration

### Database Models

#### User Profile
- Extended user model with additional fields
- Phone number and address information
- Profile picture support

#### Travel Options
- Source and destination management
- Multiple travel types (flight, bus, train)
- Operator information and pricing
- Seat availability tracking

#### Bookings
- User booking management
- Multiple passenger support
- Status tracking (pending, confirmed, cancelled)
- Payment status integration

#### Passengers
- Individual passenger information
- Age and gender details
- Seat assignment capability

### Payment Configuration

The application uses Razorpay for payment processing:

1. **Setup Razorpay Account**:
   - Sign up at [Razorpay Dashboard](https://dashboard.razorpay.com/)
   - Get your Key ID and Key Secret
   - Add them to your environment variables

2. **Payment Flow**:
   - User creates booking (status: pending)
   - Redirected to payment page
   - Razorpay payment processing
   - Webhook verification
   - Booking status updated to confirmed

## 🎯 Usage

### For Users

1. **Registration**: Create an account with email and password
2. **Browse Destinations**: Explore available travel destinations
3. **Book Travel**: Select travel options and book for multiple passengers
4. **Make Payment**: Complete payment using Razorpay (supports UPI, cards, net banking)
5. **Manage Bookings**: View and manage all bookings in the dashboard

### For Administrators

1. **Admin Panel**: Access Django admin at `/admin/`
2. **Manage Destinations**: Add/edit travel destinations
3. **Manage Travel Options**: Configure travel packages and pricing
4. **Monitor Bookings**: Track all user bookings and payments
5. **User Management**: Manage user accounts and profiles

## 🔐 Security Features

- **CSRF Protection**: All forms protected against CSRF attacks
- **Payment Verification**: Razorpay signature verification for secure payments
- **User Authentication**: Secure login/logout with session management
- **Input Validation**: Server-side validation for all user inputs
- **SQL Injection Protection**: Django ORM prevents SQL injection

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**:
   ```bash
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com
   SECRET_KEY=your-production-secret-key
   ```

2. **Static Files**:
   ```bash
   python manage.py collectstatic
   ```

3. **Database Migration**:
   ```bash
   python manage.py migrate
   ```

4. **Web Server**: Configure with Nginx/Apache + Gunicorn

### Sample Gunicorn Configuration
```bash
gunicorn --bind 0.0.0.0:8000 lykke.wsgi:application
```

### Sample Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /path/to/lykke/static/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

For coverage report:
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write descriptive commit messages
- Add tests for new features
- Update documentation as needed
- Ensure responsive design for all new UI components

## 📝 API Documentation

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Homepage |
| `/register/` | GET, POST | User registration |
| `/login/` | GET, POST | User login |
| `/destinations/` | GET | Browse destinations |
| `/book/<travel_id>/` | GET, POST | Create booking |
| `/payment/<booking_id>/` | GET | Payment page |
| `/payment/success/` | POST | Payment webhook |
| `/my-bookings/` | GET | User bookings |

## 🐛 Known Issues

- Payment webhook requires proper server configuration for production
- Image uploads need proper media file handling in production
- Email functionality requires SMTP configuration

## 📞 Support

For support and questions:
- **Email**: support@lykke.com
- **GitHub Issues**: [Create an issue](https://github.com/Parvm1102/lykke/issues)
- **Documentation**: Check this README and code comments

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django**: Web framework
- **Bootstrap**: CSS framework
- **Razorpay**: Payment gateway
- **FontAwesome**: Icons
- **MySQL**: Database system

## 📈 Future Enhancements

- [ ] Email notification system
- [ ] SMS notifications
- [ ] Advanced booking filters
- [ ] Travel itinerary management
- [ ] Review and rating system
- [ ] Multi-language support
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Loyalty program integration
- [ ] Social media integration

---

**Made with ❤️ by the Lykke Team**
