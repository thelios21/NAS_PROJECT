import ipaddress
from utils import load_json, save_json

def apply_addressing(topology_file):
    topo = load_json(topology_file)

    # LOOPBACKS
    for i, r in enumerate(sorted(topo["routers"], key=lambda x: x["name"])):
        r["loopback0"] = f"{i+1}.{i+1}.{i+1}.{i+1}"

    # préparer types des routeurs
    router_types = {r["name"]: r["type"] for r in topo["routers"]}

    # LINKS /30
    base = ipaddress.ip_network("10.0.0.0/16")
    subnets = list(base.subnets(new_prefix=30))

    for i, link in enumerate(topo["links"]):
        subnet = subnets[i]
        hosts = list(subnet.hosts())

        link["network"] = str(subnet.network_address)
        link["mask"] = "255.255.255.252"
        link["wildcard"] = "0.0.0.3"

        link["a_ip"] = str(hosts[0])
        link["b_ip"] = str(hosts[1])

        # TYPE DE LIEN (UNE SEULE FOIS)
        a_type = router_types[link["a"]]
        b_type = router_types[link["b"]]
        link["link_type"] = classify_link(a_type, b_type)

        # assign to routers
        for r in topo["routers"]:
            if r["name"] == link["a"]:
                r["interfaces"] = [
                    {**iface, "ip": link["a_ip"], "mask": link["mask"], "network": link["network"]}
                    if iface["name"] == link["a_iface"] else iface
                    for iface in r["interfaces"]
                ]
            if r["name"] == link["b"]:
                r["interfaces"] = [
                    {**iface, "ip": link["b_ip"], "mask": link["mask"], "network": link["network"]}
                    if iface["name"] == link["b_iface"] else iface
                    for iface in r["interfaces"]
                ]
    # LOOPBACK CE (automatique) - /32 comme tous les autres
    ce_index = 1
    for r in topo["routers"]:
        if r["type"] == "CE":
            r["loopback0"] = f"192.168.{ce_index}.1"
            ce_index += 1
    save_json(topology_file, topo)
    print("[OK] Addressing applied")


def classify_link(a_type, b_type):
    pair = {a_type, b_type}
    if pair == {"CE", "PE"}:
        return "access"
    if pair.issubset({"P", "PE"}):
        return "core"
    return "other"
