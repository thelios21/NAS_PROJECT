import json
import re

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def get_router_type(name):
    if name.startswith("CE"):
        return "CE"
    elif name.startswith("PE"):
        return "PE"
    elif re.match(r"^P\d+$", name):
        return "P"
    return "UNKNOWN"

def get_router_number(name):
    m = re.search(r"\d+", name)
    return int(m.group()) if m else 0

def get_interface_name(adapter, port):
    if adapter == 0:
        return f"FastEthernet{adapter}/{port}"
    else:
        return f"GigabitEthernet{adapter}/{port}"

def get_router_asn(name, rtype):
    if rtype in ["P", "PE"]:
        return 65000
    if rtype == "CE":
        m = re.search(r"\d+", name)
        if m:
            return 65100 + int(m.group())
        return 65199
    return None