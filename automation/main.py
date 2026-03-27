import os

from topology.extract_topology import extract_topology
from addressing.ipv4_plan import apply_addressing
from protocols.ospf import apply_ospf
from protocols.mpls import apply_mpls
from rendering.render_cfg import generate_configs
from inject.inject_cfg import injection_cfg
from protocols.bgp_ce_pe import apply_bgp_ce_pe
from protocols.clients import apply_clients_map
from protocols.vrf import apply_vrf
from protocols.mpbgp import apply_mpbgp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

GNS3_FILE = os.path.join(PROJECT_DIR, "NAS_TP1.gns3")
TOPO_FILE = os.path.join(BASE_DIR, "data", "topology.json")
CONFIG_DIR = os.path.join(BASE_DIR, "configs")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
CLIENTS_MAP_FILE = os.path.join(BASE_DIR, "data", "clients_map.json")

def main():
    extract_topology(GNS3_FILE, TOPO_FILE)
    apply_addressing(TOPO_FILE)
    apply_clients_map(TOPO_FILE, CLIENTS_MAP_FILE)
    apply_ospf(TOPO_FILE)
    apply_mpls(TOPO_FILE)
    apply_vrf(TOPO_FILE)
    apply_bgp_ce_pe(TOPO_FILE)
    apply_mpbgp(TOPO_FILE)
    generate_configs(TOPO_FILE, TEMPLATE_DIR, CONFIG_DIR)
    injection_cfg(PROJECT_DIR, CONFIG_DIR)

if __name__ == "__main__":
    main()