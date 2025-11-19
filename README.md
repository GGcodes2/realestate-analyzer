🏙️ Real Estate Market Analyzer (AI-Powered)

Upload Excel → Ask Anything → Get Market Insights, Trends & Predictions

This is a full-stack AI-powered real estate analysis tool that allows users to:

✅ Upload Excel datasets
✅ Ask natural language questions
✅ Automatically detect locations
✅ Get comparative analysis
✅ View trend charts
✅ View tabular filtered data
✅ Receive AI-generated insights powered by Groq Llama 3.1

🚀 Live Demo

Frontend (Vercel): https://realestate-analyzer-8olm.vercel.app

Backend API (Render): https://realestate-analyzer-vc9k.onrender.com

🧠 Features
🔹 AI Query Engine

Ask anything about the uploaded dataset:

“Compare Wakad and Baner”

“What is the price trend for Hadapsar?”

“Tell me future growth predictions for Kharadi”

AI outputs:

Market trends

Location comparison

Growth predictions

Summary insights

🔹 Excel Upload & Parsing

Upload .xlsx/.xls files.
The system then:

✔ Processes your file live (DRF)
✔ Extracts location names
✔ Loads and filters rows dynamically
✔ Prepares chart & table data

🔹 Interactive Visualizations

Trend Line Chart using Recharts

Clean summary

Table view for top 50 rows

🔹 Full-Stack Deployment

Frontend → Vercel (Static Vite Build)

Backend → Render (Django + DRF + Gunicorn + Whitenoise)

All with CORS management, secure API, Groq key support, and static file optimization.

🏗️ Project Structure
realestate-analyzer/
│
├── backend/
│   ├── api/
│   │   ├── views.py
│   │   ├── urls.py
│   ├── backend/
│   │   ├── settings.py
│   │   ├── urls.py
│   ├── realestate.xlsx (default dataset)
│   ├── render.yaml
│   └── manage.py
│
└── frontend/
    ├── src/
    │   ├── App.jsx
    ├── vite.config.js
    └── package.json

🛠️ Tech Stack
🔹 Frontend

React.js

Vite

Recharts

Tailwind (optional)

🔹 Backend

Django 5

Django REST Framework

Pandas

OpenPyXL

Whitenoise

Gunicorn

Groq LLM API

🔹 Deployment

Render (Python backend)

Vercel (React frontend)

⚙️ Installation (Local Setup)
1️⃣ Backend Setup
cd backend
pip install -r requirements.txt
python manage.py runserver

2️⃣ Frontend Setup
cd frontend
npm install
npm run dev

🔌 API Endpoints
POST /api/upload_excel/

Upload and process an Excel file.

POST /api/analyze/

Body:

{
  "query": "Compare Wakad and Baner"
}


Returns:

Summary

Trend chart data

Table data

AI insights

Detected locations

🔐 Environment Variables
Backend (.env)
GROQ_API_KEY=your_key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=*

🚢 Deployment Notes
Render Backend

Python 3.11

Uses render.yaml

Gunicorn server

Whitenoise static serving

Vercel Frontend

Set environment variable:

VITE_API_BASE=https://realestate-analyzer-vc9k.onrender.com

📸 Screenshots (Optional)

Add UI screenshots here.

🧑‍💻 Author

Gaurav Katare
BTech CSE | Full-Stack Developer
Twitter: @KGaurav_GG

⭐ Contributions

Contributions, issues, and feature requests are welcome!
