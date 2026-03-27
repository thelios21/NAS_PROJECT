from jinja2 import Environment, FileSystemLoader
from utils import load_json
import os

def generate_configs(topology_file, template_dir, output_dir):
    topo = load_json(topology_file)

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("router_ios.j2")

    os.makedirs(output_dir, exist_ok=True)

    for r in topo["routers"]:
        config = template.render(router=r)

        with open(f"{output_dir}/{r['name']}.cfg", "w") as f:
            f.write(config)

    print("[OK] Configs generated")