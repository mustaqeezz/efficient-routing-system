from lsdb import LSDB
from collections import defaultdict
import heapq

class Router:
    def __init__(self, router_id):
        self.router_id = router_id
        self.networkLSA = LSDB()
        # Define weights for each metric to compute composite cost for Dijkstra
        self.metric_weights = {
            'cost': 0.2,
            'latency': 1.0,
            'power': 0.2,
            'utilization': 0.7
        }

    def receive_lsa(self, lsa):
        self.networkLSA.add_router_lsa(lsa)

    def advertise_database(self):
        return self.networkLSA.advertise_database()

    def update_database(self, lsas):
        self.networkLSA.update_database(lsas)

    def neighbors(self):
        return self.networkLSA.neighbors(self.router_id)

    # def calculate_dijkstras(self):
    #     graph = defaultdict(list)
    #     for src in self.networkLSA.get_all_destinations():
    #         for lsa in filter(lambda l: l.link.get_src_id() == src or l.link.get_dest_id() == src, self.networkLSA.advertise_database()):
    #             # Determine the "other" endpoint of the link
    #             other = lsa.link.get_dest_id() if lsa.link.get_src_id() == src else lsa.link.get_src_id()
    #             graph[src].append((other, (lsa.cost, lsa.latency, lsa.power, lsa.utilization)))

    #     def weighted_cost(metrics):
    #         return sum(self.metric_weights[k] * v for k, v in zip(self.metric_weights.keys(), metrics))

    #     self.distances = {}
    #     self.previous = {}
    #     self.paths = {}

    #     pq = [(0, self.router_id, [self.router_id], (0,0,0,0))]
    #     visited = set()

    #     while pq:
    #         wcost, node, path, cum_metrics = heapq.heappop(pq)
    #         if node in visited:
    #             continue
    #         visited.add(node)
    #         self.distances[node] = cum_metrics
    #         self.paths[node] = path

    #         for neighbor, metrics in graph[node]:
    #             if neighbor in visited:
    #                 continue
    #             new_cum_metrics = tuple(cum + m for cum, m in zip(cum_metrics, metrics))
    #             new_wcost = weighted_cost(new_cum_metrics)

    #             # Update if new path is better
    #             old_metrics = self.distances.get(neighbor)
    #             old_wcost = weighted_cost(old_metrics) if old_metrics else float('inf')
    #             if new_wcost < old_wcost:
    #                 self.previous[neighbor] = node
    #                 heapq.heappush(pq, (new_wcost, neighbor, path + [neighbor], new_cum_metrics))

    def generate_forwarding_table(self):
        table = []
        for dest in self.networkLSA.get_all_destinations():
            if dest == self.router_id or dest not in self.distances:
                continue

            path = self.paths.get(dest)
            cost_vector = self.distances.get(dest)
            if path and cost_vector:
                table.append((dest, path, cost_vector))

        return sorted(table, key=lambda x: x[0])

def get_topology_from_user():
        print("Enter the network topology as a list of [src, dst, cost, latency, power, utilization] links:")
        print("Example: [[1, 2, 1, 10, 5, 0.7], [2, 3, 2, 20, 4, 0.6], [3, 4, 1, 15, 3, 0.5], [1, 4, 4, 40, 8, 0.9]]")

        try:
            user_input = input("Enter topology: ")
            topology = eval(user_input)
            if not isinstance(topology, list) or not all(isinstance(link, list) and len(link) == 6 for link in topology):
                raise ValueError("Invalid format")
            return topology
        except Exception as e:
            print(f"Invalid input: {e}")
            exit(1)
