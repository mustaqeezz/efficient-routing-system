
from flask import Flask, request, jsonify, render_template
from ospf import compute_standard_and_green_ospf
from router import prepare_graph_data
import json

app = Flask(__name__)

# Shared state for graph rendering and routing
network_state = {
    "topology": [],
    "weights": {},
    "routers": [],
    "standard_path": [],
    "standard_metrics": [],
    "green_path": [],
    "green_metrics": []
}

@app.route("/api/topology-file", methods=["POST"])
def upload_topology():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if not file:
        return jsonify({"error": "Empty file"}), 400

    try:
        data = json.load(file)
        topology = data.get("topology", [])
        weights = data.get("weights", {})

        if not topology:
            return jsonify({"error": "Topology is missing"}), 400

        network_state["topology"] = topology
        network_state["weights"] = weights
        return jsonify({"message": "Topology and weights stored successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/compute-paths", methods=["POST"])
def compute_paths():
    try:
        data = request.get_json()
        source = data.get("source")
        destination = data.get("destination")

        if not source or not destination:
            return jsonify({"error": "Source and destination are required."}), 400

        topology = network_state["topology"]
        weights = network_state["weights"]

        routers, std_path, std_metrics, green_path, green_metrics = compute_standard_and_green_ospf(
            topology, source, destination, weights
        )

        network_state.update({
            "routers": routers,
            "standard_path": std_path,
            "standard_metrics": std_metrics,
            "green_path": green_path,
            "green_metrics": green_metrics
        })

        return jsonify({
            "standard_ospf_path": std_path,
            "standard_metrics": std_metrics,
            "green_ospf_path": green_path,
            "green_metrics": green_metrics
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/graph-data", methods=["GET"])
def graph_data():
    data = prepare_graph_data(
        network_state["topology"],
        network_state["green_path"]
    )
    data.update({
        "standard_ospf_path": network_state["standard_path"],
        "green_ospf_path": network_state["green_path"]
    })
    return jsonify(data)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
