from pathlib import Path
from typing import Union, List
import numpy as np
from priorityQueue import PriorityQueue
from mapping import Mapping
from graph_utils import safe_zone_reached, calculate_heuristic
from utils import success_msg, error_msg


class Astar:
    risk: np.ndarray = None
    safe_cell: int = None
    cost: dict = None
    best_route: List[int] = None

    RISK_MAP = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 1,
        5: 1,
        6: 2,
        7: 2,
        8: 3,
        9: 3,
    }

    def __init__(self, start: int, grid: dict, heuristic: str = "euclidean",
                 account_risk: bool = False):
        """Initialize A* algorithm

        The "best route" is selected based on
        minimum cost (risk) encountered on the entire path,
        which is different to the typical implementation of A*, where the aim
        is to minimise the sum of the risk along the route

        'g' = distance from start node
        'h' = distance from end node
            Minimum of distances to safe zones
        'f' = the sum of the two

        For this work, largest RISK value along the path is the deciding factor

        Parameters
        ----------
        start : int
            Starting cell ID, location of a worker in an industrial cell
        grid : dict
            Map grid
        heuristic : str, Optional
            Heuristic type, diagonal, euclidean, or manhattan,
            by default euclidean
        account_risk : bool, Optional
            Perform risk-based search?, by default False
        """
        self.start = start
        self.grid = grid
        self.account_risk = account_risk
        self.heuristic = heuristic.lower()

        self._validate_grid()
        self._initialize_risk()

        # Priority queue, Open list
        # Risk - Cell IDs, lower the risk, better
        self.FRONTIER = PriorityQueue()

        # Add start to the Frontier with 0 risk
        self.FRONTIER.add(self.start)

        # Visited nodes, Closed list
        self.VISITED = set()

        # Parent (came from)
        self.PARENT = {self.start: self.start}

        # Movement costs, g costs, distance from start node
        self._initialize_movement_costs()

    def _validate_grid(self):
        n_cells = self.grid['rows'] * self.grid['columns']

        if 'safe_zones' not in self.grid or len(self.grid['safe_zones']) == 0:
            raise ValueError("Safe zones not provided!")

        for cell in self.grid['safe_zones']:
            if cell > n_cells:
                raise ValueError("Safe zone ID not matching any ID of cell in "
                                 "the provided grid")

        if n_cells != len(self.grid['cells']):
            raise ValueError(
                "Provided grid number of cells not matching rows x columns!")

        if len(self.grid['cells'][self.start]['connections']) == 0:
            raise ValueError(f"Start cell {self.start} is not a valid"
                             " traversable cell")

    def _initialize_movement_costs(self):
        # typically 'g' costs
        self.cost = {self.start: 0}
        for cell in self.grid['safe_zones']:
            self.cost[cell] = float("inf")

    def search(self):
        goal = safe_zone_reached(self.grid['safe_zones'])

        while self.FRONTIER:
            # The node with the lowest risk
            node = self.FRONTIER.pop()

            # Goal reached?
            if goal(node):
                success_msg("Path found!")
                self.safe_cell = node
                self.best_route = self._extract_best_route()

                return self.best_route

            # Node already visited?
            if node in self.VISITED:
                continue

            # Visiting the current node
            self.VISITED.add(node)

            # For each successor node (neighbors)
            for successor in self._get_successors(node):
                movement_cost = self.cost[node]

                current_cost = movement_cost \
                    + self._get_cost_of_movement(node, successor)

                if successor not in self.cost:
                    self.cost[successor] = float("inf")

                if current_cost < self.cost[successor]:
                    # Check if the successor is already in the VISITED set
                    if successor in self.VISITED:
                        continue

                    self.cost[successor] = current_cost
                    self.PARENT[successor] = node

                    # Add successor to the queue with its f-score
                    self.FRONTIER.add(
                        successor,
                        priority=self._compute_f_value(successor)
                    )

        error_msg("No path found!")
        return None

    def _compute_f_value(self, node):
        if self.account_risk:
            weight = self.risk[node]
        else:
            weight = 1

        return self.cost[node] + weight \
            * self._get_cost_of_movement(node, self.grid['safe_zones'])

    def _get_coordinates_cell(self, node):
        return np.unravel_index(
            node, (self.grid['rows'], self.grid['columns']))

    def _get_cost_of_movement(self, current: int, end: Union[List[int], int]):

        current_coord = self._get_coordinates_cell(current)

        if isinstance(end, int):
            end_coord = self._get_coordinates_cell(end)
            return calculate_heuristic(self.heuristic, current_coord,
                                       end_coord)

        min_g = float("inf")
        for zone in end:
            zone_coord = self._get_coordinates_cell(zone)
            current_g = calculate_heuristic(self.heuristic, current_coord,
                                            zone_coord)
            if current_g < min_g:
                min_g = current_g
        return min_g

    def _extract_best_route(self) -> List[int]:
        """Extract the best route

        Returns
        -------
        List[int]
            List containing IDs of cells on the best route
        """
        path = [self.safe_cell]
        current = self.safe_cell

        while True:
            current = self.PARENT[current]

            path.append(current)

            if current == self.start:
                break

        return path

    def update_risk(self, risk: Union[np.ndarray, List[int]]) -> None:
        """Updates risk

        Parameters
        ----------
        risk : Union[np.ndarray, List[int]]
            New risk array
        """
        risk = np.asarray(risk)

        if len(risk) != len(self.grid['cells']):
            raise ValueError("Length of risk array must match the number of"
                             " cells of the grid map")

        self.risk = np.maximum(risk, self.risk)

    def _initialize_risk(self):
        self.risk = np.zeros(self.grid['rows'] * self.grid['columns'])

    def _retrieve_risk(self, node: int):
        """Gets risk of cell
        Parameters
        ----------
        id : int
            ID of current cell
        """
        return self.risk[node]

    def _get_successors(self, node: int) -> List[int]:
        """Get successor ids

        Parameters
        ----------
        id : int
            ID of current cell

        Returns
        ----------
        id : List[int]
            IDs of available successor (connection) nodes
        """
        return self.grid['cells'][node]['connections']

    def animate(self, pause: float = 0.01, image: Union[str, Path] = None):
        Mapping(self.start, self.grid, pause, image).animate(
            self.best_route, self.VISITED)


if __name__ == '__main__':

    import json

    start = 39612

    # map_image = "../maps/other-maps/fictitious_map_2000cm_tested.png"

    grid = json.load(open("../maps/2-NavigationFile.json"))
    astar = Astar(start, grid, "euclidean", account_risk=True)

    # np.random.seed(20)
    risk = np.random.randint(0, 10, size=len(grid['cells']))

    astar.update_risk(risk)

    best_route = astar.search()
    print(best_route)

    astar.animate(pause=0.01, image=None)
