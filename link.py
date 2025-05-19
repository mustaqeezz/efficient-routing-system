class Link:
    def __init__(self, src_id, dest_id):
        try:
            self.src = int(src_id)
            self.dst = int(dest_id)
        except Exception as e:
            raise ValueError(f"Invalid Link IDs: src={src_id}, dst={dest_id}") from e

    def get_src_id(self):
        return self.src

    def get_dest_id(self):
        return self.dst

    def __eq__(self, other):
        return isinstance(other, Link) and (
            min(self.src, self.dst), max(self.src, self.dst)
        ) == (
            min(other.src, other.dst), max(other.src, other.dst)
        )

    def __hash__(self):
        return hash((min(self.src, self.dst), max(self.src, self.dst)))

    def __repr__(self):
        return f"Link({self.src}, {self.dst})"
