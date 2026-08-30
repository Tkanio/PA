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

def delete_user(base_url, session, userid):
    headers = {
        "Cookie": f"PVEAuthCookie={session['ticket']}",
        "CSRFPreventionToken": session['csrf_token']
    }

    resp = requests.delete(
        f"{base_url}/access/users/{userid}",
        headers=headers,
        verify=False
    )

    if resp.status_code == 200:
        print(f"Utilisateur {userid} supprimé avec succès.")
    else:
        print("Erreur lors de la suppression de l'utilisateur :", resp.status_code)
        print(resp.text)

session = authenticate(host, username, password)
userid = input(
"Entrez l'ID de l'utilisateur à supprimer (format: user@realm) : ").strip()
delete_user(base_url, session, userid)
