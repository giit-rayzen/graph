from flask import Flask, render_template, request, send_file
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    graph_image = None
    if request.method == "POST":
        # Upload file
        file = request.files["file"]
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Process the file
            df = pd.read_excel(file_path)

            # Ensure correct column names
            df.columns = ['Node A', 'Node B', 'id', 'length']

            # Validate columns
            if 'Node A' not in df.columns or 'Node B' not in df.columns or 'id' not in df.columns or 'length' not in df.columns:
                return "Error: Missing required columns in the Excel file."

            # Create edges from the DataFrame
            edges = [
                (row["Node A"], row["Node B"], {'id': row["id"], 'length': row["length"]})
                for _, row in df.iterrows()
            ]

            # Create the graph
            G = nx.Graph()  # Using undirected graph for proper edge visibility
            G.add_edges_from(edges)

            # Draw the graph with custom styling
            plt.figure(figsize=(14, 12))  # Increased figure size for better spacing

            # Position layout for nodes
            pos = nx.spring_layout(G, seed=42, k=0.5, iterations=50)  # spring_layout with custom spacing

            # Draw nodes with larger size
            nx.draw_networkx_nodes(
                G, pos, node_size=3000, node_color="lightblue", edgecolors="black"
            )

            # Draw edges with arrows and thicker edges
            nx.draw_networkx_edges(
                G, pos, edge_color="black", width=2
            )

            # Draw labels for nodes
            nx.draw_networkx_labels(
                G, pos, font_size=14, font_weight="bold", font_color="black"
            )

            # Draw edge labels for id and length with larger font
            edge_labels = {(u, v): f"id={d['id']}, len={d['length']}" for u, v, d in G.edges(data=True)}
            nx.draw_networkx_edge_labels(
                G, pos, edge_labels=edge_labels, font_size=12, font_color="darkred"
            )

            # Improve title and remove axis
            plt.title("Custom Styled Network Graph", fontsize=18)
            plt.axis("off")

            # Save the graph as an image
            graph_image = os.path.join(STATIC_FOLDER, "graph.png")
            plt.savefig(graph_image, format="PNG", bbox_inches="tight")
            plt.close()

    return render_template("index.html", graph_image=graph_image)

if __name__ == "__main__":
    app.run(debug=True)
