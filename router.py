from lsdb import LSDB
from collections import defaultdict
import heapq

class Router:
    def __init__(self, router_id):
        self.router_id = int(router_id)
        self.networkLSA = LSDB()
        # Default weights (will be overwritten per‐request in ospf.py)
        self.metric_weights = {
            'cost':        0.2,
            'latency':     1.0,
            'power':       0.2,
            'utilization': 0.7
        }
        self.distances = {}
        self.previous  = {}
        self.paths     = {}

    def receive_lsa(self, lsa):
        self.networkLSA.add_router_lsa(lsa)

    def advertise_database(self):
        return self.networkLSA.advertise_database()

    def update_database(self, lsas):
        self.networkLSA.update_database(lsas)

    def neighbors(self):
        return self.networkLSA.neighbors(self.router_id)

    def calculate_dijkstra(self):
        # Build an undirected graph with composite‐cost edges
        graph = defaultdict(list)
        for lsa in self.networkLSA.advertise_database():
            src = lsa.link.get_src_id()
            dst = lsa.link.get_dest_id()
            metrics = (lsa.cost, lsa.latency, lsa.power, lsa.utilization)
            graph[src].append((dst, metrics))
            graph[dst].append((src, metrics))

        def weighted_cost(metrics):
            return sum(self.metric_weights[k] * v
                       for k, v in zip(self.metric_weights.keys(), metrics))

        # Reset state
        self.distances = {}
        self.previous  = {}
        self.paths     = {}

        # (cum_weight, current_node, path_taken, cum_metrics)
        pq = [(0, self.router_id, [self.router_id], (0, 0, 0, 0))]
        visited = set()

        while pq:
            wcost, node, path, cum_metrics = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)

            self.distances[node] = cum_metrics
            self.paths[node]     = path

            for neighbor, metrics in graph[node]:
                if neighbor in visited:
                    continue
                new_metrics = tuple(c + m for c, m in zip(cum_metrics, metrics))
                new_wcost   = weighted_cost(new_metrics)
                old_metrics = self.distances.get(neighbor)
                old_wcost   = weighted_cost(old_metrics) if old_metrics else float('inf')

                if new_wcost < old_wcost:
                    self.previous[neighbor] = node
                    heapq.heappush(
                        pq,
                        (new_wcost, neighbor, path + [neighbor], new_metrics)
                    )

    def generate_forwarding_table(self):
        table = []
        for dest in self.networkLSA.get_all_destinations():
            if dest == self.router_id or dest not in self.paths:
                continue
            table.append((dest, self.paths[dest], self.distances[dest]))
        return sorted(table, key=lambda x: x[0])

def prepare_graph_data(topology, green_path):
    """
    Build the JSON payload for vis-network from:
      - topology: list of [src, dst, cost, latency, power, utilization]
      - green_path: list of node IDs to highlight
    """
    # Unique, sorted node IDs
    unique_nodes = sorted({
        src for src, *_ in topology
    } | {
        dst for _, dst, *_ in topology
    })

    nodes = [{"id": n, "label": str(n)} for n in unique_nodes]

    edges = []
    for src, dst, cost, latency, power, utilization in topology:
        edges.append({
            "from": src,
            "to": dst,
            "title": f"cost={cost}, lat={latency}, pwr={power}, util={utilization}"
        })

    return {
        "nodes":      nodes,
        "edges":      edges,
        "green_path": green_path
    }
