from router import Router
from link import Link
from lsa import RouterLSA

INIT_SEQ_NUM = 0x80000001


def parse_router_ids(topology):
    """
    Extract all unique router IDs from the topology list.
    """
    ids = set()
    for src, dst, *rest in topology:
        try:
            ids.add(int(src))
            ids.add(int(dst))
        except ValueError:
            raise ValueError(f"Invalid router ID in topology entry: {src}, {dst}")
    return sorted(ids)


def compute_standard_and_green_ospf(
    topology, source, destination, weights
):
    """
    Compute both standard (cost-only) and green (weighted) OSPF paths.

    Args:
        topology: List of [src, dst, cost, latency, power, utilization]
        source: Integer ID of source router
        destination: Integer ID of destination router
        weights: Dict of metric weights for green path

    Returns:
        Tuple of (routers_list, std_path, std_metrics, green_path, green_metrics)
    """
    # Initialize routers and inject LSAs
    router_ids = parse_router_ids(topology)
    routers = {rid: Router(rid) for rid in router_ids}

    for src, dst, cost, latency, power, utilization in topology:
        lsa = RouterLSA(
            Link(src, dst), INIT_SEQ_NUM,
            cost, latency, power, utilization
        )
        routers[int(src)].receive_lsa(lsa)
        routers[int(dst)].receive_lsa(lsa)

    # Synchronize LSDB across all routers
    MAX_ITER = 100
    for _ in range(MAX_ITER):
        change = False
        for rid in router_ids:
            router = routers[rid]
            advertised = router.advertise_database()
            for nbr in router.neighbors():
                neighbor = routers.get(nbr)
                if not neighbor:
                    continue
                before = set(neighbor.advertise_database())
                neighbor.update_database(advertised)
                if set(neighbor.advertise_database()) != before:
                    change = True
        if not change:
            break
    else:
        raise RuntimeError(
            f"OSPF LSDB synchronization failed after {MAX_ITER} iterations."
        )

    # Helper to compute a path given a weight map
    def _compute_path(weight_map):
        for router in routers.values():
            router.metric_weights = weight_map
            router.calculate_dijkstra()
        src_router = routers.get(int(source))
        if not src_router:
            raise ValueError(f"Source router {source} not found in topology.")
        path = src_router.paths.get(int(destination))
        metrics = src_router.distances.get(int(destination))
        
        if not path or not metrics:
            raise ValueError(f"No valid path from router {source} to router {destination}")
        
        return path, metrics

    # Standard OSPF: cost-only metrics
    std_weights = {'cost': 1.0, 'latency': 0.0, 'power': 0.0, 'utilization': 0.0}
    std_path, std_metrics = _compute_path(std_weights)

    # Green OSPF: merge user weights with defaults
    default_weights = {'cost': 0.2, 'latency': 1.0, 'power': 0.2, 'utilization': 0.7}
    green_weights = {
        k: float(weights.get(k, default_weights[k]))
        for k in default_weights
    }
    green_path, green_metrics = _compute_path(green_weights)

    return (
        list(routers.values()),
        std_path,
        std_metrics,
        green_path,
        green_metrics
    )
