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
        raise Exception("Échec de l'authentification")

def list_user(base_url, session):
    headers = {
        "Cookie": f"PVEAuthCookie={session['ticket']}",
        "CSRFPreventionToken": session['csrf_token']
    }

    resp = requests.get(
        f"{base_url}/access/users/",
        headers=headers,
        verify=False
    )
    data = resp.json()["data"]

    if resp.status_code == 200:
        print(f"Voici la liste des utilisateurs disponibles :")
        for user in data:
            print(f" - {user['userid']}")
    else:
        print("Aucun utilisateur trouvé dans la liste", resp.status_code)
        print(resp.text)

def list_group(base_url, session):
    headers = {
        "Cookie": f"PVEAuthCookie={session['ticket']}",
        "CSRFPreventionToken": session['csrf_token']
    }

    resp = requests.get(
        f"{base_url}/access/groups/",
        headers=headers,
        verify=False
    )
    data = resp.json()["data"]

    if resp.status_code == 200:
        print(f"Voici la liste des groupes disponibles :")
        for group in data:
            print(f" - {group['groupid']}")
    else:
        print("Aucun groupe trouvé dans la liste", resp.status_code)
        print(resp.text)

def add_user_to_group(base_url, session, user):
    headers = {
        "Cookie": f"PVEAuthCookie={session['ticket']}",
        "CSRFPreventionToken": session['csrf_token']
    }

    # Obtenir les groupes existants de l'utilisateur
    resp = requests.get(f"{base_url}/access/users", headers=headers, verify=False)
    existing_groups = []

    if resp.status_code == 200:
        for u in resp.json().get("data", []):
            if u["userid"] == user["userid"]:
                existing = u.get("groups", "")
                existing_groups = existing.split(",") if existing else []

    # Ajouter le groupe s'il n'existe pas déjà
    if user["group"] not in existing_groups:
        existing_groups.append(user["group"])

    # Requête PUT avec tous les groupes mis à jour
    payload = {
        "userid": user["userid"],
        "groups": ",".join(existing_groups)
    }

    resp = requests.put(
        f"{base_url}/access/users/{user['userid']}",
        headers=headers,
        data=payload,
        verify=False
    )

    if resp.status_code == 200:
        print(f"Utilisateur {user['userid']} ajouté au(x) groupe(s) : {payload['groups']}")
    else:
        print("Erreur lors de l'ajout de l'utilisateur au groupe :", resp.status_code)
        print(resp.text)

session = authenticate(host, username, password)
list_utilisateur = list_user(base_url, session)
list_groups = list_group(base_url, session)
input_user = input(
"Entrez l'ID de l'utilisateur à ajouter au groupe (format: user@realm) : "
).strip()
input_group = input("Entrez le groupe auquel ajouter l'utilisateur : ").strip()

user = {
    "userid": input_user,
    "group": input_group
}

add_user_to_group(base_url, session, user)
