from typing import Any, Tuple

class RouterLSA:
    """
    Representation of a Router Link-State Advertisement.
    Stores link information, sequence number, and associated metrics.

    Attributes:
        link: an object representing the physical link (must implement get_src_id() and get_dest_id())
        seq_num: sequence number for LSA freshness (higher is newer)
        cost: float cost metric
        latency: float latency metric
        power: float power consumption metric
        utilization: float utilization metric
    """
    def __init__(
        self,
        link: Any,
        seq_num: Any,
        cost: Any,
        latency: Any,
        power: Any,
        utilization: Any
    ) -> None:
        # Validate and store values
        if not hasattr(link, 'get_src_id') or not hasattr(link, 'get_dest_id'):
            raise TypeError(f"Invalid link object: {link!r}. Must have get_src_id() and get_dest_id().")
        self.link = link

        try:
            self.seq_num = int(seq_num)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid seq_num: {seq_num!r}, must be int.") from e

        try:
            self.cost = float(cost)
            self.latency = float(latency)
            self.power = float(power)
            self.utilization = float(utilization)
        except (TypeError, ValueError) as e:
            raise ValueError(
                f"Invalid metric types: cost={cost!r}, latency={latency!r}, "
                f"power={power!r}, utilization={utilization!r}."
            ) from e

    def metrics(self) -> Tuple[float, float, float, float]:
        """Return tuple of metrics in ('cost', 'latency', 'power', 'utilization') order."""
        return (self.cost, self.latency, self.power, self.utilization)

    def __eq__(self, other: Any) -> bool:
        """Equality if same type, link, sequence number, and identical metrics."""
        if not isinstance(other, RouterLSA):
            return False
        return (
            self.link == other.link and
            self.seq_num == other.seq_num and
            self.metrics() == other.metrics()
        )

    def __hash__(self) -> int:
        """Hash on link, sequence number, and metrics tuple."""
        return hash((self.link, self.seq_num) + self.metrics())

    def __repr__(self) -> str:
        """Unambiguous representation of the RouterLSA."""
        metrics = self.metrics()
        return (
            f"RouterLSA(link={self.link!r}, seq_num={self.seq_num}, "
            f"cost={metrics[0]}, latency={metrics[1]}, "
            f"power={metrics[2]}, utilization={metrics[3]})"
        )
