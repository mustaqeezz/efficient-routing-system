from typing import Dict, List, Tuple, Any, Iterable

class LSDB:
    """
    Link State Database for storing the latest Router LSAs.
    Each entry keyed by (src_id, dest_id) tuple for consistent hashing.
    """
    def __init__(self):
        # key: (src_id, dest_id), value: LSA instance
        self.db: Dict[Tuple[int, int], Any] = {}

    def _key(self, lsa: Any) -> Tuple[int, int]:
        """Internal: generate a tuple key for an LSA's link."""
        return (lsa.link.get_src_id(), lsa.link.get_dest_id())

    def add_router_lsa(self, lsa: Any) -> None:
        """
        Add or update the LSA if it is newer (higher seq_num).
        """
        key = self._key(lsa)
        existing = self.db.get(key)
        if existing is None or existing.seq_num < lsa.seq_num:
            self.db[key] = lsa

    def router_lsa_exists(self, lsa: Any) -> bool:
        """
        Check if an LSA with the same link and seq_num exists.
        """
        key = self._key(lsa)
        existing = self.db.get(key)
        return existing is not None and existing.seq_num == lsa.seq_num

    def advertise_database(self) -> List[Any]:
        """
        Return all stored LSAs for advertisement.
        """
        return list(self.db.values())

    def update_database(self, advertised_lsas: Iterable[Any]) -> None:
        """
        Incorporate a list of advertised LSAs into the database.
        """
        for lsa in advertised_lsas:
            self.add_router_lsa(lsa)

    def clear(self) -> None:
        """
        Clear the entire Link State Database.
        """
        self.db.clear()

    def size(self) -> int:
        """
        Return the number of unique LSAs stored.
        """
        return len(self.db)

    def get_all_destinations(self) -> List[int]:
        """
        Return a sorted list of all router IDs in the database.
        """
        routers = set()
        for lsa in self.db.values():
            routers.add(lsa.link.get_src_id())
            routers.add(lsa.link.get_dest_id())
        return sorted(routers)

    def find_connections_with(self, router_id: int) -> List[Tuple[int, float]]:
        """
        Return list of (neighbor_id, cost) for all links to/from router_id.
        """
        connections: List[Tuple[int, float]] = []
        for lsa in self.db.values():
            src = lsa.link.get_src_id()
            dst = lsa.link.get_dest_id()
            if src == router_id:
                connections.append((dst, lsa.cost))
            elif dst == router_id:
                connections.append((src, lsa.cost))
        return connections

    def neighbors(self, router_id: int) -> List[int]:
        """
        Return just the neighbor router IDs for router_id.
        """
        return [nbr for nbr, _ in self.find_connections_with(router_id)]

    def debug_print(self) -> None:
        """
        Print the current contents of the LSDB for debugging.
        """
        print("[LSDB Contents]")
        for key, lsa in self.db.items():
            src, dst = key
            print(f"  Link {src}↔{dst}: seq={lsa.seq_num}, cost={getattr(lsa, 'cost', 'N/A')}")


def extract_lsdb_data(routers: Iterable[Any]) -> List[Dict[str, Any]]:
    """
    Utility to flatten each router's advertised LSAs into JSON-serializable dicts.
    """
    all_lsas: List[Dict[str, Any]] = []
    for router in routers:
        for lsa in router.advertise_database():
            all_lsas.append({
                "src": lsa.link.get_src_id(),
                "dst": lsa.link.get_dest_id(),
                "cost": lsa.cost,
                "latency": lsa.latency,
                "power": lsa.power,
                "utilization": lsa.utilization,
                "seq_num": lsa.seq_num
            })
    return all_lsas
