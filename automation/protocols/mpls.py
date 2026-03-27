from utils import load_json, save_json

def apply_mpls(topology_file):
    topo = load_json(topology_file)

    links_by_router = {}
    for router in topo["routers"]:
        links_by_router[router["name"]] = []

    for link in topo["links"]:
        links_by_router[link["a"]].append({
            "iface": link["a_iface"],
            "link_type": link.get("link_type", "other")
        })
        links_by_router[link["b"]].append({
            "iface": link["b_iface"],
            "link_type": link.get("link_type", "other")
        })

    for r in topo["routers"]:
        if r["type"] not in ["P", "PE"]:
            continue

        core_ifaces = [
            item["iface"]
            for item in links_by_router[r["name"]]
            if item["link_type"] == "core"
        ]

        r["mpls"] = {
            "ldp": True,
            "router_id": r["loopback0"],
            "interfaces": core_ifaces
        }

    save_json(topology_file, topo)
    print("[OK] MPLS configured")