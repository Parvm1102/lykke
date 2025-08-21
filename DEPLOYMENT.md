# Lykke Travel - Production Deployment Guide

## Prerequisites
- Python 3.8+
- MySQL Database
- Render account (or any hosting platform)

## Environment Variables for Production

Set these environment variables in your hosting platform:

```bash
# Database
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=3306

# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-production-key-here
ALLOWED_HOSTS=your-domain.com

# Admin User (for first deployment)
ADMIN_USERNAME=your_admin_username
ADMIN_EMAIL=your_admin_email
ADMIN_PASSWORD=your_secure_admin_password
```

## Deployment Steps

### 1. For Render.com:

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --config gunicorn.conf.py lykke.wsgi:application`
   - **Environment**: Python 3
4. Add all environment variables in the Render dashboard
5. Deploy!

### 2. For Manual Server Deployment:

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd lykke
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables:
   ```bash
   export DEBUG=False
   export SECRET_KEY=your-secret-key
   # ... other variables
   ```

5. Run migrations and collect static files:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

6. Start the application:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

## Production Features

✅ **Gunicorn WSGI Server** - Production-ready Python server
✅ **WhiteNoise** - Static file serving without nginx
✅ **Environment-based Configuration** - Secure settings management
✅ **SSL/HTTPS Security** - Production security headers
✅ **Static File Compression** - Optimized static file delivery
✅ **Database Connection** - MySQL production database
✅ **Error Logging** - Comprehensive logging configuration
✅ **Worker Process Management** - Auto-restart and memory management

## Security Features

- HTTPS redirect in production
- Secure cookies
- XSS protection
- Content type sniffing protection
- HSTS headers
- CSRF protection

## Monitoring

The application includes:
- Gunicorn access logs
- Django error logging
- Process monitoring via Gunicorn
- Automatic worker restart on memory limits

## Scaling

To scale the application:
1. Increase worker count in `gunicorn.conf.py`
2. Add more server instances behind a load balancer
3. Use a dedicated Redis cache for sessions
4. Implement database read replicas

## Troubleshooting

Common issues and solutions:

1. **Static files not loading**: Ensure `collectstatic` was run
2. **Database connection errors**: Check environment variables
3. **502 Bad Gateway**: Check Gunicorn logs and worker configuration
4. **Memory issues**: Reduce workers or increase server resources

## Support

For deployment issues, check:
- Application logs in your hosting platform
- Gunicorn configuration
- Environment variables
- Database connectivity
