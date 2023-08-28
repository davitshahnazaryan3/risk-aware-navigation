from heapq import heappush, heappop


class PriorityQueue:
    def __init__(self, iterable=None):
        if iterable is None:
            iterable = []
            self.heap = []
            for value in iterable:
                heappush(self.heap, (0, value))

    def add(self, value: tuple, priority: int = 0):
        """Add

        Parameters
        ----------
        value : tuple
        priority : int, optional
            by default 0
        """
        heappush(self.heap, (priority, value))

    def pop(self):
        _, value = heappop(self.heap)
        return value

    def __len__(self):
        return len(self.heap)
