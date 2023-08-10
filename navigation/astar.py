"""
A* Search algorithm is one of the best and popular technique used in path-finding and graph traversals.

To approximate the shortest path in real-life situations, like- in maps, games where there can be many hindrances. We
can consider a 2D Grid having several obstacles and we start from a source cell to reach towards a goal cell.

Consider a square grid having many obstacles and we are given a starting cell and a target cell. We want to reach the
target cell (if possible) from the starting cell as quickly as possible. Here A* Search Algorithm comes to the rescue.
What A* Search Algorithm does is that at each step it picks the node according to a value-‘f’ which is a parameter equal
to the sum of two other parameters – ‘g’ and ‘h’. At each step it picks the node/cell having the lowest ‘f’, and process
that node/cell.

We define ‘g’ and ‘h’ as simply as possible below

g = the movement cost to move from the starting point to a given square on the grid, following the path generated to get
there.

h = the estimated movement cost to move from that given square on the grid to the final destination.
This is often referred to as the heuristic, which is nothing but a kind of smart guess. We really don’t know the actual
distance until we find the path, because all sorts of things can be in the way (walls, water, etc.). There can be many
ways to calculate this ‘h’ which are discussed in the later sections.

Algorithm

    1. Initialize the open list
    2. Initialize the closed list
        put starting node to the open list (can leave its f at zero)
    3. While the open list is not empty
        a) find the node with the least f on the open list, call it q
        b) pop q off the open list
        c) generate q's 8 successors and set their parents to q
        d) for each successor
            i) if successor is the goal, stop search.
            successor.g = q.g + distance between successor and q
            successor.h = distance from goal to successor (e.g., heuristics may be used - Manhattan, Diagonal and
            Euclidean Heuristics)
            successor.f = successor.g + successor.h

            ii) if a node with the same position as successor is in the OPEN list,
            which has a lower f than successor, skip this successor

            iii) if a node with the same position as successor is in the CLOSED list,
            which has a lower f than successor, skip this successor otherwise, add the node to the OPEN list
        end for loop (d)

        e) push q to the CLOSED list
        end while loop (3)

"""

from MapGenerator.env import Env
from MapGenerator.mapping import Mapping
from utils.graph_utils import *
from utils.utils import error_msg, success_msg
from navigation.priorityQueue import PriorityQueue


class Astar:
    def __init__(self, start, goal, heuristic="euclidean"):
        self.start = start
        self.goal = goal
        self.heuristic = heuristic.lower()

        if self.heuristic != "euclidean":
            error_msg("Heuristic other than euclidean is not recommended!")

        # Set up the traversable terrain and obstacles
        self.env = Env()

        # Priority queue
        self.FRONTIER = PriorityQueue()

        # Add start to the Frontier with 0 priority (highest priority)
        self.FRONTIER.add(self.start)

        # Visited nodes
        self.VISITED = set()

        # Parent (came from)
        self.PARENT = {self.start: self.start}

        # Movement costs, g cost
        self.distance = {self.start: 0, self.goal: float("inf")}

    def search(self, goal_function):

        while self.FRONTIER:
            # the node with the lowest f-value (priority)
            node = self.FRONTIER.pop()

            # Node already visited?
            if node in self.VISITED:
                continue

            # Visiting the current node
            self.VISITED.add(node)

            # Goal reached?
            if goal_function(node):
                success_msg("Path found!")
                return self.extract_path()

            # For each successor node (neighbors)
            for successor in self._successor_function(node):
                current_cost = self.distance[node] + self._get_cost_of_movement(node, successor)

                if successor not in self.distance:
                    self.distance[successor] = float("inf")

                if current_cost < self.distance[successor]:

                    self.distance[successor] = current_cost
                    self.PARENT[successor] = node

                    # Add successor into the queue with its f-score
                    self.FRONTIER.add(
                        successor,
                        priority=self._compute_f_value(successor)
                    )

        error_msg("No path found!")
        return None

    def extract_path(self):
        """
        Extract the path based on the PARENT set.
        :return: The planning path
        """
        path = [self.goal]
        current = self.goal

        while True:
            current = self.PARENT[current]
            path.append(current)

            if current == self.start:
                break

        return list(path)

    def _get_cost_of_movement(self, current, end):
        if self._is_collision(current, end):
            return float("inf")
        return calculate_heuristic(self.heuristic, current, end)

    def _is_collision(self, current, end):
        """
        Check if the line segment (current, end) is collision.
        :param current: tuple           Current node
        :param end: tuple               End node
        :return:    True: is collision
                    False: not collision
        """

        if current in self.env.obs or end in self.env.obs:
            return True

        if current[0] != end[0] and current[1] != end[1]:
            if end[0] - current[0] == current[1] - end[1]:
                s1 = (min(current[0], end[0]), min(current[1], end[1]))
                s2 = (max(current[0], end[0]), max(current[1], end[1]))
            else:
                s1 = (min(current[0], end[0]), max(current[1], end[1]))
                s2 = (max(current[0], end[0]), min(current[1], end[1]))

            if s1 in self.env.obs or s2 in self.env.obs:
                return True

        return False

    def _successor_function(self, current):
        """
        Find successor nodes of current node that does not collide with an obstacle
        :param current: tuple
        :return: list(tuple)
        """
        return [(current[0] + v[0], current[1] + v[1]) for v in self.env.movements]

    def _compute_f_value(self, current):
        """
        f = g + h, computes priority value
        :param current: tuple   Current state
        :return: float          Priority value
        """
        return self.distance[current] + calculate_heuristic(self.heuristic, current, self.goal)


if __name__ == '__main__':
    start = (20, 20)
    goal = (99, 25)

    astar = Astar(start, goal)
    mapping = Mapping(start, goal)

    # Start the search
    path = astar.search(goal_function=get_goal_function(goal))
    mapping.animate(path, astar.VISITED)
