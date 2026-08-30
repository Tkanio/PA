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

def start_vm(base_url, session, vmid):
    headers = {
        "Cookie": f"PVEAuthCookie={session['ticket']}",
        "CSRFPreventionToken": session['csrf_token']
    }

    resp = requests.post(
        f"{base_url}/nodes/{node}/qemu/{vmid}/status/start",
        headers=headers,
        verify=False
    )

    if resp.status_code == 200:
        print(f"La VM {vmid} a été démarrée avec succès.")
    else:
        print("Erreur lors du démarrage de la VM :", resp.status_code)
        print(resp.text)


session = authenticate(host, username, password)
node = input("Entrez le nom du node Proxmox : ").strip()
vmid = input("Entrez l'ID de la VM à démarrer :").strip()
start_vm(base_url, session, vmid)
