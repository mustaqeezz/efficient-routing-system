class LSDB:
    def __init__(self):
        self.db = {}

    def add_router_lsa(self, lsa):
        key = lsa.link
        try:
            if key not in self.db or self.db[key].seq_num < lsa.seq_num:
                self.db[key] = lsa
        except Exception as e:
            print(f"[ERROR] Failed processing LSA: {lsa}")
            print(f"[ERROR] LSA link: {lsa.link}, type: {type(lsa.link)}")
            print(f"[ERROR] Exception: {e}")
            raise

    def router_lsa_exists(self, lsa):
        return lsa.link in self.db and self.db[lsa.link].seq_num == lsa.seq_num

    def advertise_database(self):
        return list(self.db.values())

    def update_database(self, advertised_lsas):
        for lsa in advertised_lsas:
            self.add_router_lsa(lsa)

    def clear(self):
        self.db.clear()

    def size(self):
        return len(self.db)

    def get_all_destinations(self):
        routers = set()
        for lsa in self.db.values():
            routers.add(lsa.link.get_src_id())
            routers.add(lsa.link.get_dest_id())
        return list(routers)

    def find_connections_with(self, router_id):
        connections = []
        for lsa in self.db.values():
            if lsa.link.get_src_id() == router_id:
                connections.append((lsa.link.get_dest_id(), lsa.cost))
            elif lsa.link.get_dest_id() == router_id:
                connections.append((lsa.link.get_src_id(), lsa.cost))
        return connections

    def neighbors(self, router_id):
        return [r for r, _ in self.find_connections_with(router_id)]

    def debug_print(self):
        print("[LSDB Contents]")
        for key, val in self.db.items():
            print(f"  {key}: {val}")
