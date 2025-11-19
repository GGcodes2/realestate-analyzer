import json
import os
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response

from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_FILE = os.path.join(BASE_DIR, "realestate.xlsx")


def load_excel():
    """Load uploaded Excel from memory OR fallback file."""
    try:
        return pd.read_excel(DEFAULT_DATA_FILE)
    except Exception as e:
        raise e


def ask_groq(prompt):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a real estate analysis expert."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print("GROQ ERROR:", e)
        return None


# ----------------------------
# UPLOAD EXCEL
# ----------------------------
@csrf_exempt
@api_view(["POST"])
def upload_excel(request):
    try:
        excel_file = request.FILES.get("file")
        if not excel_file:
            return Response({"error": "No file provided"}, status=400)

        df = pd.read_excel(excel_file)
        request.session["uploaded_data"] = df.to_json()

        return Response({"message": "File uploaded successfully"})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# ----------------------------
# ANALYZE QUERY
# ----------------------------
@csrf_exempt
@api_view(["POST"])
def analyze(request):
    try:
        query = request.data.get("query", "").strip()
        if not query:
            return Response({"error": "Query required"}, status=400)

        # load excel
        df = load_excel()
        df.columns = [col.strip().lower() for col in df.columns]

        # detect locations
        locations = [
            loc for loc in df["final location"].unique()
            if isinstance(loc, str) and loc.lower() in query.lower()
        ]

        if not locations:
            locations = list(df["final location"].unique())

        filtered = df[df["final location"].str.lower().isin([l.lower() for l in locations])]

        # stats
        avg_value = filtered["total_sales - igr"].mean()

        chart = (
            filtered.groupby("year")["total_sales - igr"]
            .mean()
            .reset_index()
            .rename(columns={"year": "Year", "total_sales - igr": "Value"})
            .sort_values("Year")
            .to_dict(orient="records")
        )

        table = filtered.head(50).to_dict(orient="records")

        # AI
        ai_prompt = f"""
User Query: {query}
Locations: {locations}
Trend Data: {chart}

Analyze trends, compare locations, give future market prediction.
"""

        ai_message = ask_groq(ai_prompt)

        return Response({
            "summary": f"Locations: {locations}, Avg Value: {avg_value:.2f}",
            "chart": chart,
            "table": table,
            "ai_message": ai_message,
            "locations_used": locations,
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)
