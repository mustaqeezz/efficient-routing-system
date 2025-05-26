from typing import Any

class Link:
    """
    Represents an undirected link between two routers, identified by integer IDs.
    Equality and hashing treat the link as unordered (src↔dst).
    """
    def __init__(self, src_id: Any, dest_id: Any) -> None:
        try:
            self.src: int = int(src_id)
            self.dst: int = int(dest_id)
        except (TypeError, ValueError) as e:
            raise ValueError(
                f"Invalid Link IDs: src={src_id!r}, dst={dest_id!r}."
            ) from e

    def get_src_id(self) -> int:
        """Return the source router ID."""
        return self.src

    def get_dest_id(self) -> int:
        """Return the destination router ID."""
        return self.dst

    def __eq__(self, other: Any) -> bool:
        """
        Two links are equal if they connect the same pair of endpoints, regardless of order.
        """
        if not isinstance(other, Link):
            return False
        return {self.src, self.dst} == {other.src, other.dst}

    def __hash__(self) -> int:
        """
        Hash based on an unordered pair of endpoints, ensuring Link(a,b) == Link(b,a).
        """
        return hash((min(self.src, self.dst), max(self.src, self.dst)))

    def __repr__(self) -> str:
        """Unambiguous representation: Link(src, dest)."""
        return f"Link({self.src}, {self.dst})"
