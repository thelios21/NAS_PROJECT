import json
from utils import get_interface_name, get_router_type, get_router_asn, save_json

def extract_topology(gns3_file, output_file):
    with open(gns3_file, "r") as f:
        data = json.load(f)

    nodes = data["topology"]["nodes"]
    links = data["topology"]["links"]

    id_to_name = {}
    routers = {}

    # ROUTERS
    for n in nodes:
        if n.get("node_type") == "dynamips":
            name = n["name"]
            node_id = n["node_id"]

            id_to_name[node_id] = name
            rtype = get_router_type(name)
            routers[name] = {
                "name": name,
                "type": rtype,
                "asn": get_router_asn(name, rtype),
                "interfaces": [],
                "loopback0": None
            }

    # LINKS
    topo_links = []

    for l in links:
        a = l["nodes"][0]
        b = l["nodes"][1]

        if a["node_id"] in id_to_name and b["node_id"] in id_to_name:
            name_a = id_to_name[a["node_id"]]
            name_b = id_to_name[b["node_id"]]

            iface_a = get_interface_name(a["adapter_number"], a["port_number"])
            iface_b = get_interface_name(b["adapter_number"], b["port_number"])

            routers[name_a]["interfaces"].append({"name": iface_a})
            routers[name_b]["interfaces"].append({"name": iface_b})

            topo_links.append({
                "a": name_a,
                "a_iface": iface_a,
                "b": name_b,
                "b_iface": iface_b
            })

    topology = {
        "routers": list(routers.values()),
        "links": topo_links
    }

    save_json(output_file, topology)
    print("[OK] Topology extracted")