# Vercel Deployment Checklist

## Backend Deployment (lekha_backend)

### ✅ Pre-Deployment Checklist

- [ ] Aiven MySQL database is created and running
- [ ] Downloaded correct `ca.pem` certificate from Aiven
- [ ] `ca.pem` file is in repository root
- [ ] Obtained Gemini API key from Google AI Studio
- [ ] Updated `requirements.txt` with all dependencies
- [ ] Tested locally with `.env` file

### ✅ Vercel Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

| Variable Name | Example Value | Required |
|--------------|---------------|----------|
| `GEMINI_API_KEY` | `AIzaSyD...` | ✅ Yes |
| `DATABASE_URL` | `mysql://avnadmin:pass@host:port/db?ssl-mode=REQUIRED` | ✅ Yes |
| `ENVIRONMENT` | `production` | ✅ Yes |
| `PRODUCTION_DOMAIN` | `your-frontend.vercel.app` | ✅ Yes |
| `USE_LOCAL_DB_FALLBACK` | `false` | ⚠️ Optional |

### ✅ Deployment Steps

```bash
# 1. Navigate to backend directory
cd "D:\rent agreement checker"

# 2. Verify files are ready
git status

# 3. Deploy to Vercel
vercel --prod

# 4. Test deployment
curl https://your-backend.vercel.app/api/health
```

### ✅ Post-Deployment Verification

- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Database connection is successful
- [ ] Can register a new user
- [ ] Can login with credentials
- [ ] Can analyze a document
- [ ] Can view analysis history

---

## Frontend Deployment (lekha_frontend_code)

### ✅ Pre-Deployment Checklist

- [ ] Backend is deployed and working
- [ ] Backend URL is known
- [ ] `config.js` is included in all HTML files
- [ ] All JavaScript files use `window.API_CONFIG.ENDPOINTS`

### ✅ Vercel Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

| Variable Name | Example Value | Required |
|--------------|---------------|----------|
| `API_BASE_URL` | `https://your-backend.vercel.app` | ✅ Yes |

### ✅ Deployment Steps

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Commit environment configuration
git add .
git commit -m "Add environment configuration"
git push origin master

# 3. Deploy to Vercel
vercel --prod
```

### ✅ Post-Deployment Verification

- [ ] Landing page loads correctly
- [ ] Can open login/register modal
- [ ] Can register a new user
- [ ] Can login successfully
- [ ] Can navigate to analyzer page
- [ ] Can upload and analyze document
- [ ] Can view analysis results
- [ ] Can view analysis history
- [ ] User icon shows when logged in
- [ ] Can logout successfully

---

## CORS Configuration

### Backend CORS Setup

In `app.py`, verify CORS allows your frontend domain:

```python
allowed_origins = [
    "http://localhost:5000",
    "https://your-frontend.vercel.app",  # Add your frontend domain
]
```

If you change this, redeploy the backend.

---

## Common Issues & Solutions

### ❌ Issue: "Database connection failed"

**Check:**
- [ ] `DATABASE_URL` is set correctly in Vercel
- [ ] `ca.pem` file exists in repository
- [ ] Aiven service is running
- [ ] IP whitelist includes `0.0.0.0/0`

**Fix:**
```bash
# Verify ca.pem exists
ls -la ca.pem

# Test Aiven connection locally
python test_aiven_connection.py
```

---

### ❌ Issue: "CORS error"

**Check:**
- [ ] `PRODUCTION_DOMAIN` is set in backend
- [ ] `ENVIRONMENT=production` in backend
- [ ] Frontend domain is in `allowed_origins`

**Fix:**
Update `app.py` CORS configuration and redeploy.

---

### ❌ Issue: "API calls go to wrong URL"

**Check:**
- [ ] `API_BASE_URL` is set in frontend Vercel
- [ ] `config.js` is loaded before other scripts
- [ ] Browser console shows correct API URL

**Fix:**
```javascript
// Check in browser console:
console.log(window.API_CONFIG.BASE_URL);
// Should show: https://your-backend.vercel.app
```

---

### ❌ Issue: "Gemini API error"

**Check:**
- [ ] `GEMINI_API_KEY` is set in Vercel
- [ ] API key is valid and active
- [ ] API key has correct permissions

**Fix:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Verify or regenerate API key
3. Update in Vercel environment variables
4. Redeploy

---

## Testing Workflow

### 1. Test Backend Locally

```bash
# Create .env file
cp .env.example .env

# Edit .env with your values
# Run application
python app.py

# Test endpoints
curl http://localhost:5000/api/health
```

### 2. Test Backend on Vercel

```bash
# Deploy
vercel --prod

# Test health
curl https://your-backend.vercel.app/api/health

# Test registration
curl -X POST https://your-backend.vercel.app/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 3. Test Frontend Locally

```bash
# Serve frontend locally
cd frontend
python -m http.server 8000

# Open browser
# http://localhost:8000
```

### 4. Test Frontend on Vercel

```bash
# Deploy
vercel --prod

# Open in browser
# https://your-frontend.vercel.app

# Test all features:
# - Registration
# - Login
# - Document upload
# - Analysis
# - History
```

---

## Deployment URLs

### Backend
- **Repository:** https://github.com/jay192005/lekha_backend
- **Vercel URL:** `https://your-backend-name.vercel.app`

### Frontend
- **Repository:** https://github.com/jay192005/lekha_frontend_code
- **Vercel URL:** `https://your-frontend-name.vercel.app`

---

## Quick Deploy Commands

```bash
# Backend
cd "D:\rent agreement checker"
vercel --prod

# Frontend
cd frontend
vercel --prod
```

---

## Environment Variables Summary

### Backend (4 required)
```
GEMINI_API_KEY=your_key
DATABASE_URL=your_aiven_url
ENVIRONMENT=production
PRODUCTION_DOMAIN=your-frontend.vercel.app
```

### Frontend (1 required)
```
API_BASE_URL=https://your-backend.vercel.app
```

---

## Final Checklist

- [ ] Backend deployed to Vercel
- [ ] Backend environment variables set
- [ ] Backend health check passes
- [ ] Frontend deployed to Vercel
- [ ] Frontend environment variable set
- [ ] Frontend can connect to backend
- [ ] CORS is configured correctly
- [ ] All features tested and working
- [ ] User can register and login
- [ ] User can analyze documents
- [ ] User can view history

---

## 🎉 Success!

Once all checkboxes are complete, your application is fully deployed and ready to use!

**Share your app:**
- Frontend: `https://your-frontend.vercel.app`
- Backend API: `https://your-backend.vercel.app`
