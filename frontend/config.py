import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

MODEL_CHOICES = {
    "Llama 3.1 8B (rapide)": "llama-3.1-8b-instant",
    "Llama 3.3 70B (puissant)": "llama-3.3-70b-versatile",
    "DeepSeek-R1 Distill 70B (raisonnement)": "deepseek-r1-distill-llama-70b"
}

EXPORT_FORMATS = ["markdown", "html", "pdf"]
