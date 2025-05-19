class RouterLSA:
    def __init__(self, link, seq_num, cost, latency, power, utilization):
        self.link = link
        self.seq_num = seq_num
        self.cost = cost
        self.latency = latency
        self.power = power
        self.utilization = utilization

    def metrics(self):
        return (self.cost, self.latency, self.power, self.utilization)

    def __eq__(self, other):
        return (
            isinstance(other, RouterLSA) and
            self.link == other.link and
            self.seq_num == other.seq_num and
            self.metrics() == other.metrics()
        )

    def __hash__(self):
        return hash((self.link, self.seq_num) + self.metrics())

    def __repr__(self):
        return (f"RouterLSA(link={self.link}, seq=0x{self.seq_num:X}, cost={self.cost}, "
                f"latency={self.latency}, power={self.power}, utilization={self.utilization})")
