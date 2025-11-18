import json
import os
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from groq import Groq

# Load API key from settings (loaded from .env)
GROQ_API_KEY = settings.GROQ_API_KEY
print("DEBUG: GROQ KEY present? ", bool(GROQ_API_KEY))

groq_client = Groq(api_key=GROQ_API_KEY)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_FILE = os.path.join(BASE_DIR, "realestate.xlsx")
UPLOAD_FILE = os.path.join(BASE_DIR, "uploaded.xlsx")

# Load either uploaded file or default
def load_excel():
    if os.path.exists(UPLOAD_FILE):
        return pd.read_excel(UPLOAD_FILE)
    return pd.read_excel(DEFAULT_DATA_FILE)

# GROQ LLM call
def ask_groq(prompt):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a real estate analysis expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        print("GROQ ERROR:", e)
        return None

# UPLOAD ENDPOINT
@csrf_exempt
def upload_excel(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    if "file" not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    file = request.FILES["file"]
    with open(UPLOAD_FILE, "wb") as f:
        for chunk in file.chunks():
            f.write(chunk)

    return JsonResponse({"message": "Excel uploaded successfully"})

# ANALYZE ENDPOINT
@csrf_exempt
def analyze(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    try:
        body = json.loads(request.body)
        query = body.get("query", "").strip()
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not query:
        return JsonResponse({"error": "Query is required"}, status=400)

    # Load Excel
    try:
        df = load_excel()
        df.columns = [c.strip().lower() for c in df.columns]
    except:
        return JsonResponse({"error": "Excel file missing or corrupted"}, status=500)

    if "final location" not in df.columns:
        return JsonResponse({"error": "Column 'final location' missing"}, status=500)

    # AI: Detect locations in query
    locations = []
    for loc in df["final location"].unique():
        if isinstance(loc, str) and loc.lower() in query.lower():
            locations.append(loc)

    if not locations:
        locations = list(df["final location"].unique())

    filtered = df[df["final location"].str.lower().isin([l.lower() for l in locations])]

    if filtered.empty:
        return JsonResponse({"error": "No matching data found for your query"}, status=404)

    try:
        avg_price = filtered["total_sales - igr"].mean()
    except:
        avg_price = None

    try:
        chart = (
            filtered.groupby("year")["total_sales - igr"]
            .mean().reset_index()
            .rename(columns={"year": "Year", "total_sales - igr": "Value"})
            .sort_values("Year")
            .to_dict(orient="records")
        )
    except:
        chart = []

    lightweight_table = filtered.head(50).to_dict(orient="records")

    ai_prompt = f"""
You are a senior real-estate analyst.

User Query:
{query}

Available Data (first 50 rows):
{lightweight_table}

Detected Locations: {locations}

Trend Data:
{chart}

Your Task:
- Perform deep comparison (if multiple locations)
- Identify price trends, demand signals
- Predict future growth
- Keep answer short and high-quality (5–7 sentences)

Answer:
"""

    ai_output = ask_groq(ai_prompt) or "AI unavailable."

    table = filtered.to_dict(orient="records")

    return JsonResponse({
        "summary": f"Detected locations: {locations}. Avg sales value: {avg_price:.2f}."
        if avg_price else f"Detected locations: {locations}.",
        "chart": chart,
        "table": table,
        "ai_message": ai_output,
        "locations_used": locations,
    })
