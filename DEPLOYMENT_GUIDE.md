# Deployment Guide — StockPilot IMS

This guide explains how to deploy **StockPilot IMS** to the web so you can access it online and share the link with your professor.

---

## ⚠️ Important Note: Netlify vs. Python Flask Applications

**Netlify** is a platform built exclusively for **static websites and frontend frameworks** (HTML, CSS, JavaScript, React, Vue) and Node.js serverless functions. 
Netlify **does not natively support running persistent Python backend web servers (Flask)** or local SQLite databases.

If you attempt to deploy a dynamic Python Flask app directly on Netlify:
- Netlify will fail to find an `index.html` file or static build folder.
- There is no persistent Python runtime to execute `app.py` or `gunicorn`.
- Any local SQLite database changes cannot be persisted on static CDNs.

---

## 🚀 Recommended Solution: Deploying to Render (Free & Native Python Support)

**[Render.com](https://render.com/)** is the modern equivalent of Netlify, but purpose-built for **Python, Flask, and database applications**. It offers:
- **Free Tier** for Web Services.
- **Direct GitHub Integration** (auto-deploys every time you push code to GitHub, just like Netlify).
- Automatic SSL certificates (`https://your-app.onrender.com`).
- Pre-configured support with the included [`Procfile`](file:///d:/Vs%20Code%20Programs/Inventory-management-system/Procfile) and [`render.yaml`](file:///d:/Vs%20Code%20Programs/Inventory-management-system/render.yaml).

### Step-by-Step Deployment on Render (Takes ~2 minutes)

1. **Push your changes to GitHub:**
   ```bash
   git add .
   git commit -m "Add deployment configuration files"
   git push origin main
   ```

2. **Log into Render:**
   - Go to **[https://render.com/](https://render.com/)**.
   - Click **"Get Started"** or **"Log In"** and choose **"Sign in with GitHub"**.

3. **Create a New Web Service:**
   - In your Render Dashboard, click the **"New +"** button at the top and select **"Web Service"**.
   - Select your repository: `harshalmus/Inventory-management-system` and click **"Connect"**.

4. **Configure the Service Settings:**
   Render will automatically detect the settings from our [`render.yaml`](file:///d:/Vs%20Code%20Programs/Inventory-management-system/render.yaml), but if asked:
   - **Name:** `stockpilot-ims` (or any name you prefer)
   - **Region:** Singapore / Frankfurt / Oregon (choose closest to you)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free`

5. **Environment Variables (Optional):**
   Under **Environment Variables**, add:
   - `SECRET_KEY`: `your-random-secret-key-12345`
   - `PYTHON_VERSION`: `3.12.8`

6. **Deploy:**
   - Click **"Create Web Service"**.
   - Render will build the virtual environment, install dependencies, seed the demo database, and start the Gunicorn server.
   - Within 1–2 minutes, your site will be live at:  
     `https://stockpilot-ims.onrender.com`

---

## ⚡ Alternative: Deploying to Vercel

If you prefer Vercel (which operates similarly to Netlify but supports Python serverless functions via `@vercel/python`):

1. Go to **[https://vercel.com/](https://vercel.com/)** and log in with GitHub.
2. Click **"Add New Project"** and import `harshalmus/Inventory-management-system`.
3. Vercel will automatically detect [`vercel.json`](file:///d:/Vs%20Code%20Programs/Inventory-management-system/vercel.json) and deploy the Flask app as a serverless function.

*Note: For applications relying on SQLite, Render is superior to Vercel because Render provides a persistent container process.*

---

## 🔑 Default Login Credentials on Live Deployment

Once deployed, you can immediately log into the web app using the pre-seeded demo accounts:

| Role | Username | Password |
|---|---|---|
| **Administrator** | `admin` | `admin123` |
| **Staff Member** | `staff` | `staff123` |

