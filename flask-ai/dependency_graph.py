import os
from typing import List, Dict
from pyvis.network import Network
import networkx as nx
import re


def generate_dependency_graph(file_data: List[Dict[str, str]], output_path: str = "repo_graph.html") -> str:
    try:
        G = nx.DiGraph()

        # First pass: add all nodes
        for file in file_data:
            G.add_node(file['path'])

        # Second pass: add dependency edges based on imports
        for file in file_data:
            src_path = file['path']
            content = file['content']
            for target in file_data:
                tgt_path = target['path']
                if tgt_path != src_path:
                    tgt_name = os.path.splitext(os.path.basename(tgt_path))[0]  # remove extension

                    # Basic dependency detection via imports or API call references
                    patterns = [
                        rf"\bimport\s+{tgt_name}\b",
                        rf"\bfrom\s+{tgt_name}\b",
                        rf"require\(['\"]{tgt_name}['\"]\)",
                        rf"fetch\(['\"].*/{tgt_name}['\"]\)",
                        rf"axios\.\w+\(['\"].*/{tgt_name}['\"]\)",
                        rf"requests\.\w+\(['\"].*/{tgt_name}['\"]\)"
                    ]

                    for pattern in patterns:
                        if re.search(pattern, content):
                            G.add_edge(src_path, tgt_path)
                            break

        print("Dependency edges created.")

        net = Network(
            notebook=False,
            directed=True,
            height="800px",
            width="100%",
            bgcolor="#222",
            font_color="white"
        )

        # Physics-based layout for smooth interactions
        net.barnes_hut()
        net.toggle_physics(True)

        # Convert to pyvis from networkx
        net.from_nx(G)

        # Add neighbor (dependency) info to node tooltips
        neighbor_map = net.get_adj_list()
        for node in net.nodes:
            neighbors = neighbor_map[node["id"]]
            node["title"] = f"<b>{node['id']}</b><br>Imports/Imported by:<br>" + "<br>".join(neighbors)
            node["value"] = len(neighbors)  # Node size based on number of dependencies
            node["color"] = "#00bfff" if len(neighbors) > 0 else "#aaaaaa"

        # Show physics control UI
        net.show_buttons(filter_=["physics"])

        os.makedirs("static", exist_ok=True)
        output_file = os.path.join("static", output_path)
        net.write_html(output_file)

        print(f"Graph saved to: {output_file}")
        return f"/static/{output_path}"

    except Exception as e:
        print(f"[ERROR in generate_dependency_graph]: {e}")
        raise
