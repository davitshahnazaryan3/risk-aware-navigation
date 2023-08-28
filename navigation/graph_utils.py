import math


def calculate_heuristic(heuristic: str, current, goal) -> float:
    """Calculates the heuristic
    Manhattan:
        Calculated based on distance between two points along the axes of the
        grid lines
        Allowed to move only in 4 directions (right, left, bottom, top)
        Might overestimate the distance between a state and the states
        diagonally accessible to it
    Euclidean:
        Calculated as the length of a straight line formed between two points
        Allowed to move in any direction
        Best choice, never overestimates
        Might underestimate if there is an obstacle to avoid on th eline
        between current and destination nodes
    Diagonal:
        Allowed to move only in 8 directions.

    Parameters
    ----------
    heuristic : str
        Heuristic type
    current : _type_
        Current state
    goal : _type_
        Goal node

    Returns
    -------
    float
        Heuristic distance

    Raises
    ------
    ValueError
        Wrong heuristic type is provided
    """
    dx = abs(goal[0] - current[0])
    dy = abs(goal[1] - current[1])

    if heuristic.lower() == "manhattan":
        return dx + dy
    elif heuristic.lower() == "euclidean":
        return math.hypot(goal[0] - current[0], goal[1] - current[1])
    elif heuristic.lower() == "diagonal":
        # octile distance: D=1, D2=sqrt(2)
        return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)
    else:
        raise ValueError("Wrong heuristic type, must be: manhattan, "
                         "diagonal or euclidean!")


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


def safe_zone_reached(safe_zones):
    def is_target(cell):
        return cell in safe_zones
    return is_target
