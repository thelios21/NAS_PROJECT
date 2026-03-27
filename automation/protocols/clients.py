from utils import load_json, save_json

def apply_clients_map(topology_file, clients_map_file):
    topo = load_json(topology_file)
    clients_map = load_json(clients_map_file)

    routers = {r["name"]: r for r in topo["routers"]}

    # 1. Ajouter client_id sur les CE
    for r in topo["routers"]:
        if r["type"] == "CE":
            entry = clients_map.get(r["name"], {})
            r["client_id"] = entry.get("client_id")

    # 2. Marquer les liens access avec le client_id du CE
    for link in topo["links"]:
        a = routers[link["a"]]
        b = routers[link["b"]]

        if a["type"] == "CE" and b["type"] == "PE":
            link["client_id"] = a.get("client_id")
        elif a["type"] == "PE" and b["type"] == "CE":
            link["client_id"] = b.get("client_id")

    save_json(topology_file, topo)
    print("[OK] Client mapping applied")