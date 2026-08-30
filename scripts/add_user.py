import requests
import urllib3
import os
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

host = os.getenv("HOST")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
base_url = f"https://{host}:8006/api2/json"

def authenticate(host, username, password):
    url = f"https://{host}:8006/api2/json/access/ticket"
    resp = requests.post(url, data={"username": username, "password": password}, verify=False)

    if resp.status_code == 200:
        token = resp.json()["data"]
        return {
            "ticket": token["ticket"],
            "csrf_token": token["CSRFPreventionToken"]
        }
    else:
        print(f"Status: {resp.status_code}")
        print(f"Réponse: {resp.text}")
        raise Exception("Échec de l'authentification")

def create_user(base_url, session, user):
    headers = {
        "Cookie": f"PVEAuthCookie={session['ticket']}",
        "CSRFPreventionToken": session['csrf_token']
    }
    payload = {
        "userid": user["userid"],
        "password": user["password"],
    }

    resp = requests.post(
        f"{base_url}/access/users",
        headers=headers,
        data=payload,
        verify=False
    )

    if resp.status_code == 200:
        print(f"Utilisateur {user['userid']} créé avec succès.")
    else:
        print("Erreur lors de la création de l'utilisateur :", resp.status_code)
        print(resp.text)

session = authenticate(host, username, password)
input_user = input(
"Entrez l'ID de l'utilisateur à créer (format: user@realm) : ").strip()
input_password = input("Entrez le mot de passe de l'utilisateur : ").strip()
user = {
    "userid": input_user,
    "password": input_password,
}
create_user(base_url, session, user)
