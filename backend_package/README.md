# Agreement Checker Backend

Flask backend API for the lekha.ai Agreement Checker application.

## 🚀 Features

- **Document Analysis**: AI-powered analysis using Google Gemini
- **User Management**: Registration, login, and history tracking
- **Database Integration**: MySQL with Aiven cloud support
- **Data Management**: APIs for deleting and managing data
- **Security**: Input validation, SQL injection prevention
- **Health Monitoring**: Health check endpoints

## 📁 Project Structure

```
backend/
├── app.py                    # Main Flask application
├── ai.py                     # AI analysis module
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel deployment config
├── .env.example             # Environment variables template
├── databases/               # Database schemas
│   ├── data.sql
│   └── analysis_history.sql
├── tests/                   # Test files
│   ├── test_api.py
│   ├── test_aiven_connection.py
│   └── test_deletion_api.py
└── docs/                    # Documentation
    ├── AIVEN_SETUP.md
    ├── GET_CA_CERTIFICATE.md
    └── DEPLOYMENT.md
```

## 🛠️ Setup

### Local Development

1. **Clone repository**
   ```bash
   git clone https://github.com/jay192005/agreement-checker-backend-.git
   cd agreement-checker-backend-
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Setup database**
   ```bash
   python setup_database.py
   ```

5. **Run application**
   ```bash
   python app.py
   ```

### Production Deployment (Vercel)

1. **Setup Aiven Database** (see `docs/AIVEN_SETUP.md`)
2. **Configure environment variables** in Vercel
3. **Deploy** via Vercel GitHub integration

## 🔧 API Endpoints

### Health Check
- `GET /api/health` - System health status

### Document Analysis
- `POST /api/analyze` - Analyze rental agreement

### User Management
- `POST /api/register` - User registration
- `POST /api/login` - User authentication
- `GET /api/history/<email>` - Get analysis history

### Data Management
- `POST /api/delete-data` - Delete data from tables
- `POST /api/clear-history` - Clear analysis history

## 🔒 Environment Variables

```env
# Database Configuration
DATABASE_URL=mysql://user:pass@host:port/db?ssl-mode=REQUIRED
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=rent_agreements_db
DB_PORT=3306

# API Keys
GEMINI_API_KEY=your_gemini_api_key

# Environment
ENVIRONMENT=development
USE_LOCAL_DB_FALLBACK=true
```

## 🧪 Testing

```bash
# Test API functionality
python tests/test_api.py

# Test database connection
python tests/test_aiven_connection.py

# Test deletion APIs
python tests/test_deletion_api.py
```

## 📚 Documentation

- [Aiven Database Setup](docs/AIVEN_SETUP.md)
- [CA Certificate Guide](docs/GET_CA_CERTIFICATE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details