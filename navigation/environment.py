class Environment:
    def __init__(self, rows, columns):
        # Map size
        self.rows = rows
        self.columns = columns

        # Generate obstacles, case study specific
        self.obs = self._generate_obstacles()

    def _generate_obstacles(self):
        """
        Initialize obstacles' positions
        """
        x = self.columns
        y = self.rows
        obs = set()

        # Peripheral walls
        for i in range(x):
            obs.add((i, 0))
        for i in range(x):
            obs.add((i, y - 1))

        for i in range(y):
            obs.add((0, i))
        for i in range(y):
            obs.add((x - 1, i))

        return obs
