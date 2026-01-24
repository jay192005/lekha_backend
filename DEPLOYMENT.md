# Deployment Guide for lekha.ai

## 🚀 Local Development

### Prerequisites
- Python 3.13+
- MySQL Server 8.0+

### Steps
1. Clone repository and install dependencies (see README.md)
2. Run `python app.py`
3. Access at `http://localhost:5000`

## ☁️ Production Deployment

### Vercel Deployment (Recommended)

#### 1. Setup Aiven Database
- Create MySQL service on [Aiven Console](https://console.aiven.io/)
- Download CA certificate (`ca.pem`)
- Create database and tables using provided SQL files

#### 2. Configure Environment Variables
Set in Vercel Dashboard:
```env
DATABASE_URL=mysql://avnadmin:password@host.aivencloud.com:port/defaultdb?ssl-mode=REQUIRED
GEMINI_API_KEY=your_gemini_api_key
ENVIRONMENT=production
```

#### 3. Deploy
- Connect GitHub repository to Vercel
- Deploy automatically

### Docker Deployment (Alternative)

#### Dockerfile
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

## 🔧 Production Configuration

### Security
- Use HTTPS only
- Never commit sensitive data
- Use strong database passwords
- Implement rate limiting

### Performance
Use production WSGI server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔍 Health Check

Test deployment: `GET /api/health`

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## 📞 Support

For issues:
1. Check `/api/health` endpoint
2. Review application logs
3. Create GitHub issue