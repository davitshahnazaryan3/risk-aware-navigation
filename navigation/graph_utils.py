import math


def calculate_heuristic(heuristic, current, goal):
    """
    Calculates the heuristic
    Manhattan:
        Calculated based on distance between two points along the axes of the grid lines
        Allowed to move only in 4 directions (right, left, bottom, top)
        Might overestimate the distance between a state and the states diagonally accessible to it
    Euclidean:
        Calculated as the length of a straight line formed between two points
        Allowed to move in any direction
        Best choice, never overestimates
        Might underestimate if there is an obstacle to avoid on th eline between current and destination nodes
    Diagonal:
        Allowed to move only in 8 directions.
        Not implemented
    :param heuristic: string        Heuristic type
    :param current: tuple           Current state
    :param goal: tuple              Goal node
    :return: float                  Heuristic distance
    """
    if heuristic == "manhattan":
        return abs(goal[0] - current[0]) + abs(goal[1] - current[1])
    elif heuristic == "euclidean":
        return math.hypot(goal[0] - current[0], goal[1] - current[1])
    else:
        raise ValueError("Wrong heuristic type, must be: manhattan, euclidean!")


def get_goal_function(target):
    """
    Function to check if we have reached the goal cell
    check if current cell is equal to target
    """
    def is_target(cell):
        return cell == target
    return is_target


def reconstruct_path(parent, start, end):
    reverse_path = [end]
    while end != start:
        end = parent[end]
        reverse_path.append(end)
    return list(reversed(reverse_path))

