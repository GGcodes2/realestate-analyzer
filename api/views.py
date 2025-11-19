import json
import os
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from groq import Groq

# ----------------------------------------
# ENV Key
# ----------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default bundled Excel file
DEFAULT_DATA_FILE = os.path.join(BASE_DIR, "realestate.xlsx")


# ----------------------------------------
# LOAD EXCEL (Render Safe)
# ----------------------------------------
def load_excel():
    """
    Load Excel either from memory cache or fallback file.
    Render free tier cannot write to disk -> so we store uploaded data in memory.
    """
    global uploaded_df

    if uploaded_df is not None:
        return uploaded_df

    return pd.read_excel(DEFAULT_DATA_FILE)


# In-memory dataframe (global)
uploaded_df = None


# ----------------------------------------
# Ask AI (Groq)
# ----------------------------------------
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


# ----------------------------------------
# UPLOAD EXCEL (Render Safe)
# ----------------------------------------
@csrf_exempt
@api_view(["POST"])
def upload_excel(request):
    global uploaded_df

    try:
        excel_file = request.FILES.get("file")

        if not excel_file:
            return Response({"error": "No file uploaded"}, status=400)

        # Read Excel directly from memory
        uploaded_df = pd.read_excel(excel_file)

        return Response({"message": "File uploaded successfully!"})
    except Exception as e:
        return Response({"error": f"Upload failed: {str(e)}"}, status=500)


# ----------------------------------------
# ANALYZE
# ----------------------------------------
@csrf_exempt
@api_view(["POST"])
def analyze(request):
    try:
        query = request.data.get("query", "").strip()
    except:
        return Response({"error": "Invalid JSON"}, status=400)

    if not query:
        return Response({"error": "Query is required"}, status=400)

    # Load data
    try:
        df = load_excel()
        df.columns = [c.strip().lower() for c in df.columns]
    except Exception as e:
        return Response({"error": f"Excel load error: {str(e)}"}, status=500)

    if "final location" not in df.columns:
        return Response({"error": "Excel missing required column: final location"}, status=500)

    # Detect locations
    locations = []
    for loc in df["final location"].dropna().unique():
        if isinstance(loc, str) and loc.lower() in query.lower():
            locations.append(loc)

    if not locations:
        locations = list(df["final location"].dropna().unique())

    # Filter rows
    filtered = df[df["final location"].str.lower().isin([l.lower() for l in locations])]

    if filtered.empty:
        return Response({"error": "No matching data found"}, status=404)

    # Compute stats
    avg_sales = None
    if "total_sales - igr" in filtered.columns:
        avg_sales = filtered["total_sales - igr"].mean()

    # Chart
    chart = []
    if "year" in filtered.columns and "total_sales - igr" in filtered.columns:
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

    # Prepare AI prompt
    sample_rows = filtered.head(50).to_dict(orient="records")

    ai_prompt = f"""
User Query: {query}

Locations Detected: {locations}

Filtered Data Sample:
{sample_rows}

Trend Data:
{chart}

Task:
- Deeply answer the user's real estate query
- Compare locations, growth, demand, and pricing
- Analyze trends and future predictions
- Provide 5–7 strong insights
"""

    ai_output = ask_groq(ai_prompt) or "AI unavailable."

    return Response({
        "summary": f"Detected: {locations}" + (f", Avg Sales: {avg_sales:.2f}" if avg_sales else ""),
        "chart": chart,
        "table": filtered.to_dict(orient="records"),
        "ai_message": ai_output,
        "locations_used": locations,
    })
