import requests
import urllib3
import os
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

host = os.getenv("HOST")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
base_url = f"https://{host}:8006/api2/json"

vm_cpu_usage = Gauge('vm_cpu_usage_percent', 'CPU usage of VM', ['vm_name'])
vm_mem_used = Gauge('vm_memory_used_megabytes', 'Used memory of VM (MB)', ['vm_name'])
vm_mem_total = Gauge('vm_memory_total_megabytes', 'Total memory of VM (MB)', ['vm_name'])
vm_disk_used = Gauge('vm_disk_used_gigabytes', 'Used disk space of VM (GB)', ['vm_name'])
vm_disk_total = Gauge('vm_disk_total_gigabytes', 'Total disk space of VM (GB)', ['vm_name'])
vm_net_rx = Gauge('vm_network_rx_megabytes', 'Network RX (received) MB of VM', ['vm_name'])
vm_net_tx = Gauge('vm_network_tx_megabytes', 'Network TX (sent) MB of VM', ['vm_name'])
vm_uptime = Gauge('vm_uptime_seconds', 'Uptime of VM in seconds', ['vm_name'])



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

session = authenticate(host, username, password)
def get_all_vms_detailed_metrics(host, base_url, session):
    headers = {
        "Cookie": f"PVEAuthCookie={session['ticket']}",
        "CSRFPreventionToken": session['csrf_token']
    }

    resp_nodes = requests.get(f"{base_url}/nodes", headers=headers, verify=False)
    if resp_nodes.status_code != 200:
        print("Impossible de récupérer les nodes :", resp_nodes.status_code)
        return

    nodes = resp_nodes.json()["data"]

    for node in nodes:
        node_name = node["node"]
        print(f"\n====== Node : {node_name} ======\n")

        resp_vms = requests.get(f"{base_url}/nodes/{node_name}/qemu", headers=headers, verify=False)
        if resp_vms.status_code != 200:
            print(f"Erreur lors de la récupération des VMs sur {node_name}")
            continue

        vms = resp_vms.json()["data"]
        for vm in vms:
            vmid = vm["vmid"]
            vm_name = vm.get("name", f"vm_{vmid}")

            resp_stat = requests.get(f"{base_url}/nodes/{node_name}/qemu/{vmid}/status/current", headers=headers, verify=False)
            if resp_stat.status_code == 200:
                stat = resp_stat.json()["data"]

                cpu = stat.get("cpu", 0) * 100
                mem = stat.get("mem", 0) / (1024 ** 2)
                maxmem = stat.get("maxmem", 0) / (1024 ** 2)
                disk = stat.get("disk", 0) / (1024 ** 3)
                maxdisk = stat.get("maxdisk", 0) / (1024 ** 3)
                netin = stat.get("netin", 0) / (1024 ** 2)
                netout = stat.get("netout", 0) / (1024 ** 2)
                uptime = stat.get("uptime", 0)

                print(f"--- VM {vmid} : {vm_name} ---")
                print(f"CPU usage   : {cpu:.2f}%")
                print(f"RAM         : {mem:.1f} / {maxmem:.1f} Mo")
                print(f"Disk        : {disk:.2f} / {maxdisk:.2f} Go")
                print(f"Net RX / TX : {netin:.2f} / {netout:.2f} Mo")
                print(f"Uptime      : {uptime} s")
                print("-" * 50)

                # MISE À JOUR DES MÉTRIQUES
                vm_cpu_usage.labels(vm_name).set(cpu)
                vm_mem_used.labels(vm_name).set(mem)
                vm_mem_total.labels(vm_name).set(maxmem)
                vm_disk_used.labels(vm_name).set(disk)
                vm_disk_total.labels(vm_name).set(maxdisk)
                vm_net_rx.labels(vm_name).set(netin)
                vm_net_tx.labels(vm_name).set(netout)
                vm_uptime.labels(vm_name).set(uptime)
            else:
                print(f"Impossible de lire l’état de la VM {vmid} ({vm_name})")

if __name__ == "__main__":
    print("Serveur Prometheus en écoute sur le port 8000...")
    start_http_server(8000)
    import time

    while True:
        try:
            session = authenticate(host, username, password)
            get_all_vms_detailed_metrics(host, base_url, session)
        except Exception as e:
            print(f"Erreur de collecte : {e}")
        time.sleep(30)