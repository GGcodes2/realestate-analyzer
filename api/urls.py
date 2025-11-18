from django.urls import path
from .views import analyze, upload_excel

urlpatterns = [
    path("analyze/", analyze),
    path("upload_excel/", upload_excel),
]
