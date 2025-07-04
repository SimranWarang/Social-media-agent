📊 Social Media Agent – Landing Platform

This repository hosts the Landing App for our AI-powered Instagram automation tools built during our internship at Digital Dojo Pvt. Ltd.

Apps Overview:
- CM Social Media Agent – React + Flask-based Instagram Scheduler
- SR Social Media Agent – Streamlit-based Instagram Generator

────────────────────────────
🧩 Folder Structure:

SAFINAL/
├── landing-app/          # Main dashboard + login system
├── app1-frontend/        # React frontend for App 1
├── app1-backend/         # Flask backend with Gemini/OpenAI + Meta API
├── SA_STREAMLIT/         # Streamlit caption generator (App 2)

────────────────────────────
🚀 Features:

- AI-generated captions using Gemini or OpenAI
- Image fetching via DuckDuckGo CSE
- Instagram auto-posting and scheduling via Meta Graph API
- Full-stack with modern design and routing
- Clerk authentication + Vercel deployment

────────────────────────────
🧪 Environment Variables Setup:

In landing-app/.env

VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
VITE_BACKEND_URL=http://localhost:5000

In app1-backend/.env

# === Google Gemini / Generative AI ===
GOOGLE_API_KEY=your_google_gemini_api_key

# === google images Custom Search (via Google CSE) ===
GOOGLE_CSE_API_KEY=your_google_cse_api_key
GOOGLE_CSE_ID=your_google_cse_id

# === Instagram Auto Posting ===
ACCESS_TOKEN=your_instagram_graph_api_access_token
IG_USER_ID=your_instagram_user_id

# === OpenAI (Optional) ===
OPENAI_API_KEY=your_openai_api_key

────────────────────────────
💻 Local Development:

1. Install dependencies

# React frontend
cd landing-app
npm install

# Flask backend
cd ../app1-backend
pip install -r requirements.txt

2. Run the apps

# Backend
cd app1-backend
python flask_app.py

# Frontend (Vite)
cd ../landing-app
npm run dev

Open your browser and go to http://localhost:5173

────────────────────────────
🌐 Deployment on Vercel:

1. Push the landing-app/ to GitHub
2. Import into vercel.com
3. Set the following Vercel environment variables:

VITE_CLERK_PUBLISHABLE_KEY
VITE_BACKEND_URL

Framework: Vite  
Build command: npm run build  
Output directory: dist

────────────────────────────
👥 Team:

- Simran Warang
- Chinar Mhatre  
- Riya Divekar
