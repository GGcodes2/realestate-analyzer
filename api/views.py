import json
import os
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from groq import Groq

# ───────────────────────────────────────────────
# ENV KEY
# ───────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# IMPORTANT FOR RENDER FREE TIER
UPLOAD_FILE = "/tmp/uploaded.xlsx"     # temporary storage
DEFAULT_DATA_FILE = os.path.join(BASE_DIR, "realestate.xlsx")


# Load Excel
def load_excel():
    if os.path.exists(UPLOAD_FILE):
        return pd.read_excel(UPLOAD_FILE)
    return pd.read_excel(DEFAULT_DATA_FILE)


# Groq call
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


# ───────────────────────────────────────────────
# FILE UPLOAD ENDPOINT
# ───────────────────────────────────────────────
@csrf_exempt
def upload_excel(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    if "file" not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    file = request.FILES["file"]

    # save to /tmp
    with open(UPLOAD_FILE, "wb") as f:
        for chunk in file.chunks():
            f.write(chunk)

    return JsonResponse({"message": "Excel uploaded successfully"})


# ───────────────────────────────────────────────
# AI ANALYZE ENDPOINT
# ───────────────────────────────────────────────
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

    # Load dataset
    try:
        df = load_excel()
        df.columns = [c.strip().lower() for c in df.columns]
    except Exception as e:
        return JsonResponse({"error": f"Excel error: {str(e)}"}, status=500)

    if "final location" not in df.columns:
        return JsonResponse({"error": "Column 'final location' missing"}, status=500)

    # Detect referenced locations
    locations = []
    for loc in df["final location"].unique():
        if isinstance(loc, str) and loc.lower() in query.lower():
            locations.append(loc)

    # fallback: use whole dataset
    if not locations:
        locations = list(df["final location"].unique())

    filtered = df[df["final location"].str.lower().isin([l.lower() for l in locations])]

    if filtered.empty:
        return JsonResponse({"error": "No matching data found"}, status=404)

    # Stats
    try:
        avg_price = filtered["total_sales - igr"].mean()
    except:
        avg_price = None

    # Chart data
    try:
        chart = (
            filtered.groupby("year")["total_sales - igr"]
            .mean()
            .reset_index()
            .rename(columns={"year": "Year", "total_sales - igr": "Value"})
            .sort_values("Year")
            .to_dict(orient="records")
        )
    except:
        chart = []

    lightweight_table = filtered.head(50).to_dict(orient="records")

    # AI SUPER PROMPT
    ai_prompt = f"""
User Query:
{query}

Detected Locations:
{locations}

Filtered Data (first 50 rows):
{lightweight_table}

Trend Data:
{chart}

Task:
- Understand user's question deeply
- Compare multiple locations if mentioned
- Analyze trends, growth, pricing, demand
- Predict future market performance
- Give a clear real-estate insight (5–7 sentences)
"""

    ai_output = ask_groq(ai_prompt) or "AI unavailable."

    table = filtered.to_dict(orient="records")

    return JsonResponse({
        "summary": f"Locations Detected: {locations}. Avg Sales Value: {avg_price:.2f}" if avg_price else f"Locations Detected: {locations}",
        "chart": chart,
        "table": table,
        "ai_message": ai_output,
        "locations_used": locations,
    })
