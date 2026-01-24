# Aiven Database Setup for Vercel Deployment

## Step 1: Create Aiven Account and MySQL Service

1. Go to [Aiven Console](https://console.aiven.io/)
2. Sign up for a free account
3. Create a new MySQL service:
   - Choose MySQL 8.0
   - Select a cloud provider (AWS, Google Cloud, or Azure)
   - Choose a region close to your users
   - Select the free tier plan

## Step 2: Download SSL Certificate

1. Go to your MySQL service in Aiven Console
2. Click on "Overview" tab
3. Download the **CA Certificate** (`ca.pem`)
4. Place `ca.pem` in your project's root folder (same level as `app.py`)

## Step 3: Get Database Connection Details

1. In your MySQL service, go to "Connection information"
2. Copy the **Service URI** (it looks like):
   ```
   mysql://avnadmin:password@your-service-name.aivencloud.com:12345/defaultdb
   ```

## Step 4: Create Your Database and Tables

1. Connect to your Aiven MySQL using the Aiven Console or a MySQL client
2. Run these SQL commands:

```sql
-- Create the database
CREATE DATABASE rent_agreements_db;
USE rent_agreements_db;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create analysis_history table
CREATE TABLE analysis_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    analysis_result JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## Step 5: Update Your Requirements.txt

Make sure your `requirements.txt` includes:

```txt
mysql-connector-python==8.1.0
```

## Step 6: Set Up Vercel Environment Variables

1. Go to your Vercel Dashboard
2. Select your project
3. Go to Settings > Environment Variables
4. Add these variables:

```env
DATABASE_URL=mysql://avnadmin:your_password@your-service.aivencloud.com:port/rent_agreements_db
GEMINI_API_KEY=your_gemini_api_key_here
ENVIRONMENT=production
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your_production_secret_key_here
```

## Step 7: Deploy to Vercel

1. Make sure `ca.pem` is in your project root
2. Push your code to GitHub
3. Deploy via Vercel (it will automatically detect the changes)

## Step 8: Test Your Deployment

### Test Database Connection:
```bash
curl https://your-app.vercel.app/api/health
```

### Test Data Deletion (Example):
```bash
# Delete specific user's analysis history
curl -X POST https://your-app.vercel.app/api/clear-history \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Truncate entire analysis_history table
curl -X POST https://your-app.vercel.app/api/delete-data \
  -H "Content-Type: application/json" \
  -d '{
    "table": "analysis_history",
    "operation": "truncate"
  }'

# Delete specific records
curl -X POST https://your-app.vercel.app/api/delete-data \
  -H "Content-Type: application/json" \
  -d '{
    "table": "users",
    "operation": "delete",
    "conditions": {"email": "user@example.com"}
  }'
```

## API Endpoints for Data Management

### 1. Delete Data Endpoint
**POST** `/api/delete-data`

**Request Body:**
```json
{
  "table": "users",           // Required: "users" or "analysis_history"
  "operation": "delete",      // Required: "delete" or "truncate"
  "conditions": {             // Required for DELETE, ignored for TRUNCATE
    "email": "user@example.com"
  }
}
```

**Response:**
```json
{
  "message": "Successfully deleted data from users",
  "table": "users",
  "operation": "delete",
  "affected_rows": 1
}
```

### 2. Clear Analysis History
**POST** `/api/clear-history`

**Request Body:**
```json
{
  "email": "user@example.com"  // Optional: if provided, clears only this user's history
}
```

## Troubleshooting

### SSL Connection Issues
- **Error**: "SSL connection error"
- **Solution**: Ensure `ca.pem` is in your project root and deployed to Vercel

### Database Connection Timeout
- **Error**: "Connection timeout"
- **Solution**: Check that you've whitelisted all IPs (0.0.0.0/0) in Aiven

### Transaction Not Committed
- **Error**: "Data not actually deleted"
- **Solution**: The code includes `connection.commit()` - this should work automatically

### Invalid Table Name
- **Error**: "Table not allowed"
- **Solution**: Only `users` and `analysis_history` tables are allowed for security

## Security Features

1. **Table Whitelist**: Only specific tables can be deleted
2. **SQL Injection Prevention**: Parameterized queries used
3. **Column Name Validation**: Prevents malicious column names
4. **Transaction Control**: Proper commit/rollback handling
5. **SSL Encryption**: All connections use SSL with certificate validation

## File Structure After Setup

```
your-project/
├── app.py                 # Main Flask app with deletion routes
├── ca.pem                 # Aiven SSL certificate (REQUIRED)
├── requirements.txt       # Including mysql-connector-python
├── vercel.json           # Vercel configuration
├── .env                  # Local environment (not deployed)
└── .env.example          # Template for environment variables
```

## Why This Works

1. **SSL Certificate**: `ca.pem` enables secure connection to Aiven
2. **DATABASE_URL**: Single environment variable contains all connection info
3. **Transaction Commit**: `connection.commit()` ensures changes are saved
4. **Error Handling**: Comprehensive try/catch blocks with rollback
5. **Security**: Input validation and parameterized queries prevent SQL injection