import requests, json

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNzc4OTYwNzUxfQ.uX1ctpnwWzm1egyZHCWNBN6BkOxsPFUatqkVTTGIFJc"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Lister les conversations
try:
    r = requests.get("http://localhost:8000/conversations", headers=headers)
    print("Statut:", r.status_code)
    print("Réponse:", r.text)
except Exception as e:
    print("Erreur:", e)