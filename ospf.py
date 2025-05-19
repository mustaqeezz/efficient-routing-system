from router import Router
from link import Link
from lsa import RouterLSA
from lsdb import LSDB                  #for dijkstra
from collections import defaultdict    #for dijkstra
import heapq                           #for dijkstra

INIT_SEQ_NUM = 0x80000001

def parse_router_ids(topology):
    router_ids = set()
    for src, dst, *_ in topology:
        router_ids.add(src)
        router_ids.add(dst)
    return sorted(list(router_ids))

def synchronize_routers(network_topology):
    router_ids = parse_router_ids(network_topology)
    routers = {rid: Router(rid) for rid in router_ids}

    # Step 1: Inject direct LSAs with multiple metrics into each router
    for src, dst, cost, latency, power, utilization in network_topology:
        lsa = RouterLSA(Link(src, dst), INIT_SEQ_NUM, cost, latency, power, utilization)
        routers[src].receive_lsa(lsa)
        routers[dst].receive_lsa(lsa)

    # Step 2: Flood LSAs until synchronized or iteration limit is reached
    MAX_ITER = 100
    for _ in range(MAX_ITER):
        converged = True
        for rid in router_ids:
            router = routers[rid]
            advertised = router.advertise_database()
            for neighbor_id in router.neighbors():
                if neighbor_id not in routers:
                    continue
                neighbor = routers[neighbor_id]
                before = set(neighbor.advertise_database())
                neighbor.update_database(advertised)
                after = set(neighbor.advertise_database())
                if before != after:
                    converged = False
        if converged:
            return [routers[r] for r in router_ids]
    raise RuntimeError("OSPF LSDB synchronization failed after 100 iterations.")

def print_forwarding_tables(routers):
    print("\n==== Forwarding Tables ====")
    for router in routers:
        calculate_dijkstras(router)
        print(f"\nRouter {router.router_id} Forwarding Table:")
        table = router.generate_forwarding_table()
        for dest, path, cost_vector in table:
            cost_str = ", ".join(f"{name}: {val}" for name, val in zip(["cost", "latency", "power", "utilization"], cost_vector))
            print(f"  Dest: {dest}, Path: {' -> '.join(map(str, path))}, Metrics: {cost_str}")

def print_preferred_path(routers, src, dst):
    router_map = {r.router_id: r for r in routers}
    if src not in router_map or dst not in router_map:
        print("Source or destination router not found")
        return
    router = router_map[src]
    calculate_dijkstras(router)
    path = router.paths.get(dst)
    if not path:
        print(f"No path from {src} to {dst}")
        return
    cost_vector = router.distances.get(dst)
    cost_str = ", ".join(f"{name}: {val}" for name, val in zip(["cost", "latency", "power", "utilization"], cost_vector))
    print(f"Preferred path from {src} to {dst}: {' -> '.join(map(str, path))}")
    print(f"Metrics: {cost_str}")

def calculate_dijkstras(router):
        graph = defaultdict(list)
        for src in router.networkLSA.get_all_destinations():
            for lsa in filter(lambda l: l.link.get_src_id() == src or l.link.get_dest_id() == src, router.networkLSA.advertise_database()):
                # Determine the "other" endpoint of the link
                other = lsa.link.get_dest_id() if lsa.link.get_src_id() == src else lsa.link.get_src_id()
                graph[src].append((other, (lsa.cost, lsa.latency, lsa.power, lsa.utilization)))

        def weighted_cost(metrics):
            return sum(router.metric_weights[k] * v for k, v in zip(router.metric_weights.keys(), metrics))

        router.distances = {}
        router.previous = {}
        router.paths = {}

        pq = [(0, router.router_id, [router.router_id], (0,0,0,0))]
        visited = set()

        while pq:
            wcost, node, path, cum_metrics = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)
            router.distances[node] = cum_metrics
            router.paths[node] = path

            for neighbor, metrics in graph[node]:
                if neighbor in visited:
                    continue
                new_cum_metrics = tuple(cum + m for cum, m in zip(cum_metrics, metrics))
                new_wcost = weighted_cost(new_cum_metrics)

                # Update if new path is better
                old_metrics = router.distances.get(neighbor)
                old_wcost = weighted_cost(old_metrics) if old_metrics else float('inf')
                if new_wcost < old_wcost:
                    router.previous[neighbor] = node
                    heapq.heappush(pq, (new_wcost, neighbor, path + [neighbor], new_cum_metrics))