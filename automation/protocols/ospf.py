from utils import load_json, save_json

def apply_ospf(topology_file):
    topo = load_json(topology_file)

    # Index pratique
    links_by_router = {}
    for router in topo["routers"]:
        links_by_router[router["name"]] = []

    for link in topo["links"]:
        links_by_router[link["a"]].append({
            "iface": link["a_iface"],
            "network": link["network"],
            "wildcard": link["wildcard"],
            "link_type": link.get("link_type", "other")
        })
        links_by_router[link["b"]].append({
            "iface": link["b_iface"],
            "network": link["network"],
            "wildcard": link["wildcard"],
            "link_type": link.get("link_type", "other")
        })

    for r in topo["routers"]:
        if r["type"] == "CE":
            continue

        networks = []

        for item in links_by_router[r["name"]]:
            if item["link_type"] == "core":
                networks.append({
                    "network": item["network"],
                    "wildcard": item["wildcard"]
                })

        networks.append({
            "network": r["loopback0"],
            "wildcard": "0.0.0.0"
        })

        r["ospf"] = {
            "process_id": 1,
            "router_id": r["loopback0"],
            "networks": networks
        }

    save_json(topology_file, topo)
    print("[OK] OSPF configured")