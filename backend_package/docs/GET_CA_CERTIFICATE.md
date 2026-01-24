# How to Download Aiven CA Certificate

## 🎯 **CRITICAL STEP**: You need the real CA certificate for SSL connection to work!

### Step 1: Go to Aiven Console
1. Open your browser and go to [Aiven Console](https://console.aiven.io/)
2. Log in to your account
3. Click on your MySQL service: **your-mysql-service-name**

### Step 2: Download CA Certificate
1. In your MySQL service dashboard, click on the **"Overview"** tab
2. Scroll down to find the **"Connection information"** section
3. Look for **"CA Certificate"** 
4. Click **"Download"** next to CA Certificate
5. Save the file as `ca.pem`

### Step 3: Replace the Placeholder File
1. The downloaded file should be named `ca.pem`
2. Copy this file to your project root directory (same folder as `app.py`)
3. Replace the existing placeholder `ca.pem` file

### Step 4: Verify the Certificate
The real certificate file should start with:
```
-----BEGIN CERTIFICATE-----
```

And end with:
```
-----END CERTIFICATE-----
```

If your `ca.pem` file contains comments like "PLACEHOLDER" or "Download the CA Certificate", it's not the real certificate!

### Step 5: Test Your Connection
Run the test script to verify everything works:

```bash
python test_aiven_connection.py
```

## 🚨 **Common Issues:**

### Issue 1: "SSL Access Denied"
- **Cause**: Missing or incorrect CA certificate
- **Solution**: Download the real `ca.pem` from Aiven Console

### Issue 2: "Connection Refused" 
- **Cause**: Wrong host or port
- **Solution**: Verify your connection details match:
  - Host: `mysql-service-name.aivencloud.com`
  - Port: `PORT_NUMBER`

### Issue 3: "Access Denied for User"
- **Cause**: Wrong credentials or IP not whitelisted
- **Solution**: 
  - Check username in your `.env` file
  - Check password in your `.env` file
  - Verify IP whitelist includes `0.0.0.0/0`

## 📋 **Your Aiven Connection Details:**
Configure these in your `.env` file:
- **Service URI**: Use DATABASE_URL environment variable
- **Host**: Your Aiven MySQL host
- **Port**: Your Aiven MySQL port
- **User**: Your Aiven username
- **Password**: Your Aiven password (keep this secret!)
- **Database**: `defaultdb` (we'll create `rent_agreements_db`)
- **SSL Mode**: `REQUIRED`

## ✅ **Next Steps After Getting Certificate:**
1. Download real `ca.pem` certificate
2. Run `python test_aiven_connection.py` to test
3. Create database tables if needed
4. Test your Flask app locally
5. Deploy to Vercel with the certificate