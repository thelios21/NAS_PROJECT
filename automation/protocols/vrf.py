from utils import load_json, save_json

def apply_vrf(topology_file):
    topo = load_json(topology_file)

    # Liste triée des clients connus
    client_ids = sorted({
        link.get("client_id")
        for link in topo["links"]
        if link.get("link_type") == "access" and link.get("client_id")
    })

    client_to_index = {
        client_id: i + 1
        for i, client_id in enumerate(client_ids)
    }

    routers = {r["name"]: r for r in topo["routers"]}

    # Initialisation
    for r in topo["routers"]:
        if r["type"] == "PE":
            r["vrfs"] = []

    # Construire les VRF nécessaires par PE
    for link in topo["links"]:
        if link.get("link_type") != "access":
            continue

        client_id = link.get("client_id")
        if not client_id:
            continue

        idx = client_to_index[client_id]
        rd = f"65000:{idx}"
        rt = f"65000:{idx}"

        a = routers[link["a"]]
        b = routers[link["b"]]

        if a["type"] == "PE" and b["type"] == "CE":
            pe = a
            pe_iface = link["a_iface"]
        elif a["type"] == "CE" and b["type"] == "PE":
            pe = b
            pe_iface = link["b_iface"]
        else:
            continue

        # Attacher l'interface PE à la VRF
        for iface in pe["interfaces"]:
            if iface["name"] == pe_iface:
                iface["vrf"] = client_id

        # Ajouter la VRF si absente
        if not any(v["name"] == client_id for v in pe["vrfs"]):
            pe["vrfs"].append({
                "name": client_id,
                "rd": rd,
                "rt_import": rt,
                "rt_export": rt
            })

    save_json(topology_file, topo)
    print("[OK] VRF configured")