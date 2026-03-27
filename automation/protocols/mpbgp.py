from utils import load_json, save_json

def apply_mpbgp(topology_file):
    topo = load_json(topology_file)

    pes = [r for r in topo["routers"] if r["type"] == "PE"]

    for pe in pes:
        pe["bgp"] = pe.get("bgp", {
            "enabled": True,
            "asn": pe.get("asn"),
            "neighbors": [],
            "vpnv4_neighbors": []
        })
        pe["bgp"]["enabled"] = True
        pe["bgp"]["asn"] = pe.get("asn")
        pe["bgp"].setdefault("neighbors", [])
        pe["bgp"].setdefault("vpnv4_neighbors", [])

    for i in range(len(pes)):
        for j in range(i + 1, len(pes)):
            pe1 = pes[i]
            pe2 = pes[j]

            pe1["bgp"]["vpnv4_neighbors"].append({
                "ip": pe2["loopback0"],
                "remote_as": pe2["asn"],
                "description": pe2["name"],
                "update_source": "Loopback0"
            })

            pe2["bgp"]["vpnv4_neighbors"].append({
                "ip": pe1["loopback0"],
                "remote_as": pe1["asn"],
                "description": pe1["name"],
                "update_source": "Loopback0"
            })

    save_json(topology_file, topo)
    print("[OK] MP-BGP vpnv4 configured")