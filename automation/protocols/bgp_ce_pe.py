from utils import load_json, save_json

def apply_bgp_ce_pe(topology_file):
    topo = load_json(topology_file)

    routers = {r["name"]: r for r in topo["routers"]}

    # =========================
    # INIT BGP STRUCTURE
    # =========================
    for r in topo["routers"]:
        r["bgp"] = r.get("bgp", {
            "enabled": False,
            "asn": r.get("asn"),
            "neighbors": [],
            "vpnv4_neighbors": [],
            "networks": []
        })

        r["bgp"]["enabled"] = r["bgp"].get("enabled", False)
        r["bgp"]["asn"] = r.get("asn")
        r["bgp"].setdefault("neighbors", [])
        r["bgp"].setdefault("vpnv4_neighbors", [])
        r["bgp"].setdefault("networks", [])

    # =========================
    # ASN UNIQUE POUR CE
    # =========================
    ce_list = sorted([r for r in topo["routers"] if r["type"] == "CE"], key=lambda x: x["name"])

    for i, ce in enumerate(ce_list):
        ce_asn = 65000 + i + 1
        ce["asn"] = ce_asn
        ce["bgp"]["asn"] = ce_asn

    # =========================
    # BGP CE <-> PE
    # =========================
    for link in topo["links"]:
        if link.get("link_type") != "access":
            continue

        a = routers[link["a"]]
        b = routers[link["b"]]
        client_id = link.get("client_id")

        if a["type"] == "CE" and b["type"] == "PE":
            ce = a
            pe = b
            ce_ip = link["a_ip"]
            pe_ip = link["b_ip"]
        elif a["type"] == "PE" and b["type"] == "CE":
            pe = a
            ce = b
            pe_ip = link["a_ip"]
            ce_ip = link["b_ip"]
        else:
            continue

        # =========================
        # CE CONFIG
        # =========================
        ce["bgp"]["enabled"] = True

        # éviter doublons voisins
        if not any(n["ip"] == pe_ip for n in ce["bgp"]["neighbors"]):
            ce["bgp"]["neighbors"].append({
                "ip": pe_ip,
                "remote_as": pe["asn"],
                "description": pe["name"],
                "vrf": None,
                "activate_in_vrf": False
            })

        # annoncer loopback automatiquement
        if ce.get("loopback0"):
            if not any(
                n["network"] == ce["loopback0"] and n["mask"] == "255.255.255.255"
                for n in ce["bgp"]["networks"]
            ):
                ce["bgp"]["networks"].append({
                    "network": ce["loopback0"],
                    "mask": "255.255.255.255"
                })
        # =========================
        # PE CONFIG
        # =========================
        pe["bgp"]["enabled"] = True

        if not any(n["ip"] == ce_ip for n in pe["bgp"]["neighbors"]):
            pe["bgp"]["neighbors"].append({
                "ip": ce_ip,
                "remote_as": ce["asn"],
                "description": ce["name"],
                "vrf": client_id,
                "activate_in_vrf": True
            })

    save_json(topology_file, topo)
    print("[OK] CE-PE BGP configured")