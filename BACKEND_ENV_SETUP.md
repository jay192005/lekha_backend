# Backend Environment Variables Setup Guide

## Required Environment Variables for Deployment

### 1. **GEMINI_API_KEY** (Required)
Your Google Gemini API key for AI-powered document analysis.

**How to get it:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

**Example:**
```
GEMINI_API_KEY=AIzaSyD...your_actual_key_here
```

---

### 2. **DATABASE_URL** (Required for Production)
Complete Aiven MySQL connection string with SSL.

**Format:**
```
DATABASE_URL=mysql://username:password@host:port/database?ssl-mode=REQUIRED
```

**Your Aiven Details:**
1. Go to [Aiven Console](https://console.aiven.io/)
2. Select your MySQL service
3. Copy the "Service URI" from the Overview tab

**Example:**
```
DATABASE_URL=mysql://avnadmin:YOUR_ACTUAL_PASSWORD@mysql-xxxxx-yourservice.h.aivencloud.com:10102/defaultdb?ssl-mode=REQUIRED
```

---

### 3. **ENVIRONMENT** (Required)
Specifies the deployment environment.

**Values:**
- `development` - Local development
- `production` - Production deployment

**For Vercel:**
```
ENVIRONMENT=production
```

---

### 4. **PRODUCTION_DOMAIN** (Required for Production)
Your frontend domain for CORS configuration.

**Example:**
```
PRODUCTION_DOMAIN=your-frontend-app.vercel.app
```

---

### 5. **USE_LOCAL_DB_FALLBACK** (Optional)
Whether to fall back to local database if Aiven connection fails.

**Values:**
- `true` - Enable fallback
- `false` - Disable fallback (recommended for production)

**For Production:**
```
USE_LOCAL_DB_FALLBACK=false
```

---

## Optional Environment Variables

### Local Database Configuration (Development Only)

```bash
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_local_mysql_password
DB_NAME=rent_agreements_db
DB_PORT=3306
```

### OCR Configuration (Not available on Vercel)

```bash
POPPLER_PATH=C:\path\to\poppler\bin
```

---

## Setting Environment Variables in Vercel

### Method 1: Vercel Dashboard

1. Go to your Vercel project
2. Click on "Settings"
3. Navigate to "Environment Variables"
4. Add each variable:
   - **Name:** Variable name (e.g., `GEMINI_API_KEY`)
   - **Value:** Your actual value
   - **Environment:** Select "Production", "Preview", and "Development"
5. Click "Save"

### Method 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Add environment variables
vercel env add GEMINI_API_KEY
vercel env add DATABASE_URL
vercel env add ENVIRONMENT
vercel env add PRODUCTION_DOMAIN
vercel env add USE_LOCAL_DB_FALLBACK
```

---

## Complete Production Environment Variables

Copy these to your Vercel environment variables (replace with your actual values):

```bash
# Required
GEMINI_API_KEY=AIzaSyD...your_actual_key_here
DATABASE_URL=mysql://avnadmin:YOUR_PASSWORD@your-mysql-host.aivencloud.com:10102/defaultdb?ssl-mode=REQUIRED
ENVIRONMENT=production
PRODUCTION_DOMAIN=your-frontend-app.vercel.app

# Optional
USE_LOCAL_DB_FALLBACK=false
```

---

## SSL Certificate (ca.pem)

The `ca.pem` file is already included in your repository. Make sure it's the correct Aiven CA certificate.

**To verify:**
1. The file should start with `-----BEGIN CERTIFICATE-----`
2. The file should end with `-----END CERTIFICATE-----`

**If you need to update it:**
1. Go to Aiven Console
2. Select your MySQL service
3. Download the CA Certificate
4. Replace the `ca.pem` file in your repository
5. Commit and push the changes

---

## Testing Your Configuration

### 1. Test Locally

Create a `.env` file in your project root:

```bash
GEMINI_API_KEY=your_key_here
DATABASE_URL=your_aiven_connection_string
ENVIRONMENT=development
```

Run the application:
```bash
python app.py
```

### 2. Test on Vercel

After setting environment variables:

```bash
# Deploy to Vercel
vercel --prod

# Check deployment logs
vercel logs
```

### 3. Test API Endpoints

```bash
# Health check
curl https://your-backend.vercel.app/api/health

# Should return:
# {"status": "healthy", "database": "connected", "message": "All systems operational"}
```

---

## Troubleshooting

### Issue: "Database connection failed"
**Solution:**
- Verify `DATABASE_URL` is correct
- Check if `ca.pem` is the correct certificate
- Ensure Aiven service is running
- Verify IP whitelist includes `0.0.0.0/0`

### Issue: "GEMINI_API_KEY not found"
**Solution:**
- Verify environment variable is set in Vercel
- Check variable name is exactly `GEMINI_API_KEY`
- Redeploy after setting the variable

### Issue: "CORS error from frontend"
**Solution:**
- Verify `PRODUCTION_DOMAIN` is set correctly
- Check `ENVIRONMENT=production`
- Update CORS configuration in `app.py` if needed

### Issue: "SSL handshake failed"
**Solution:**
- Download fresh `ca.pem` from Aiven Console
- Verify the certificate file is not corrupted
- Check that `ssl-mode=REQUIRED` is in `DATABASE_URL`

---

## Security Best Practices

1. **Never commit `.env` files** - They contain sensitive information
2. **Use strong passwords** - For database and API keys
3. **Rotate keys regularly** - Update API keys periodically
4. **Limit IP access** - Use Aiven IP whitelist when possible
5. **Use HTTPS only** - Never use HTTP in production
6. **Monitor logs** - Check Vercel logs for suspicious activity

---

## Quick Reference

### Minimum Required Variables for Vercel Deployment:

```
GEMINI_API_KEY=your_gemini_key
DATABASE_URL=your_aiven_connection_string
ENVIRONMENT=production
PRODUCTION_DOMAIN=your-frontend-domain.vercel.app
```

### Files Needed in Repository:

- `app.py` - Main application
- `ai.py` - AI analysis logic
- `requirements.txt` - Python dependencies
- `vercel.json` - Vercel configuration
- `ca.pem` - SSL certificate
- `.env.example` - Environment template (for reference)

---

## Next Steps After Configuration

1. Set all environment variables in Vercel
2. Verify `ca.pem` is correct
3. Deploy to Vercel: `vercel --prod`
4. Test health endpoint
5. Test authentication endpoints
6. Test document analysis
7. Update frontend `API_BASE_URL` to point to your backend

---

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Verify all environment variables are set
3. Test database connection separately
4. Check Aiven service status
5. Review CORS configuration
