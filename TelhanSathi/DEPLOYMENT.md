# TelhanSathi Deployment Guide

## Recommended: Render.com (Free Tier)

Render is the best free option for your Flask project as it supports:
- ✅ Free tier hosting (hibernates after 15 min inactivity)
- ✅ PostgreSQL database (free tier)
- ✅ WebSocket support (for Flask-SocketIO)
- ✅ Automatic deployments from GitHub
- ✅ SSL/TLS certificates included
- ✅ Cron jobs support

---

## Step 1: Prepare Your Repository

### 1.1 Ensure all files are in git
```bash
git add -A
git commit -m "Prepare for Render deployment"
git push origin main
```

### 1.2 Create `.env` file locally (never commit this)
```bash
cp .env.example .env
# Edit .env with your actual values
```

---

## Step 2: Deploy to Render

### 2.1 Create Render Account
1. Go to https://render.com/
2. Sign up with GitHub
3. Accept authorization

### 2.2 Connect Your GitHub Repository
1. Dashboard → New → Web Service
2. Select "Connect a repository"
3. Choose your TelhanSathi repository
4. Fill in:
   - **Name**: `telhan-sathi`
   - **Environment**: `Python 3.11`
   - **Build Command**: 
     ```
     pip install -r requirements.txt && python -m flask db upgrade
     ```
   - **Start Command**: 
     ```
     gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT wsgi:app
     ```
   - **Plan**: `Free`

### 2.3 Configure Environment Variables
In Render Dashboard:
1. Go to your service → Environment
2. Add all variables from `.env.example`:
   ```
   SECRET_KEY=your-random-secret-key
   FLASK_ENV=production
   DATABASE_URL=<Will be provided by Render PostgreSQL>
   GOOGLE_APPLICATION_CREDENTIALS=<Your Google creds>
   TWILIO_ACCOUNT_SID=<Your Twilio SID>
   TWILIO_AUTH_TOKEN=<Your Twilio Token>
   ```

### 2.4 Add PostgreSQL Database
1. Dashboard → New → PostgreSQL
2. Set **Plan** to `Free`
3. Name: `telhan-sathi-db`
4. Copy the connection string to your Render service's `DATABASE_URL` env var

### 2.5 Deploy
1. Click "Create Web Service"
2. Render will automatically deploy from your GitHub repo
3. View logs in real-time during deployment

---

## Step 3: Post-Deployment

### 3.1 Initialize Database
After first deployment, run migrations:
```bash
# Use Render's Shell/Console to run:
python -m flask db upgrade
```

### 3.2 Test Your App
- Visit your Render URL (e.g., `https://telhan-sathi.onrender.com`)
- Check logs if there are errors: Dashboard → Logs

### 3.3 Set Up GitHub Webhook
- Render automatically creates this
- Push to main branch = automatic deployment

---

## Alternative Free Options

### PythonAnywhere
- **Pros**: Easiest for Python apps, custom domain support
- **Cons**: Limited free resources
- **Setup**: https://www.pythonanywhere.com/ (follow web2py guide)

### Railway
- **Pros**: Generous free tier ($5/month credit), simple interface
- **Cons**: Credit depletes
- **Setup**: Similar to Render, push from GitHub

### Vercel + FastAPI
- **Pros**: Very fast, serverless
- **Cons**: Not ideal for long-running WebSockets
- **Not recommended** for your Flask-SocketIO needs

---

## Important Notes

### WebSocket Support
- Render supports WebSockets out of the box ✅
- Using `eventlet` worker for Flask-SocketIO compatibility
- No additional configuration needed

### Database Considerations
- Free tier PostgreSQL has limits (~400 connections, 1GB storage)
- For production scale, upgrade plan
- Automatic backups included

### Cost When Scaling
- Free tier dormancy: ~$0/month
- Standard tier (always on): ~$10/month
- Database (free): included
- Database (growth): ~$15/month for PostgreSQL

### Troubleshooting

**Build fails:**
- Check: `pip install -r requirements.txt` locally passes
- Verify Python version compatibility

**Database errors:**
- Run migrations manually in Shell
- Check DATABASE_URL in environment

**WebSocket not working:**
- Verify Flask-SocketIO configured correctly
- Check CORS settings in app.py

**App too slow:**
- Free tier has CPU limits
- Upgrade to paid tier for better performance

---

## Monitoring & Maintenance

### View Logs
Render Dashboard → Logs (real-time streaming)

### Health Checks
- Render pings `/` by default
- Ensure your root route is responsive

### Auto-redeploy on Push
- Already configured via GitHub webhook
- Just `git push` your changes

---

## Security Checklist

- [ ] Change `SECRET_KEY` to a random string
- [ ] Set `FLASK_ENV=production`
- [ ] Enable `SESSION_COOKIE_SECURE=True` (change in app.py for production)
- [ ] Store API keys in environment variables
- [ ] Never commit `.env` or credentials
- [ ] Use PostgreSQL instead of SQLite in production
- [ ] Enable HTTPS (automatic on Render)

---

## Next Steps

1. Follow **Step 2.1-2.4** above
2. Push code to GitHub
3. Monitor deployment logs
4. Test your application
5. Share your public URL

Good luck! 🚀
