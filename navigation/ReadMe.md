# The Modified A* Algorithm

Risk-aware route is computed based on the client's starting position from two data structures: the **risk-map** and the **routes-graph** (directed graph representing all the walkable paths). 

The map (grid) area is modelled into discrete cells which consider the physical characteristics of the environment, like the walls and the emergency exits. The map is a .json file with cell information in terms of its connectivity to other cells, with identifications from left to right and up to bottom approach. Two cells are connected if there is no wall between them. The red door is one-way.

![discrete_map](../img/discrete_map.png)

When the risk map is received from Risk Calculation module, the weight of the nodes in the routes-graph are updated. High risk transfers to high weight. An **adaptation of the A* algorithm** is used, where the best route is computed from the current user's position to each safe area and the best route among them is selected.

**Best route** is defiend as the route that minimises the maximum risk value encountered, different from typical A*, where the aim is to minimise the sum of the risk along the route. For example, if route A has a risk of 9 but all 1's, while route B has all 4's, the best route will be the route B, since we don't want the user to pass through a very dangerous (risk 9) area. Additionally, no importance is given to metric distance for the scope. Only, maximum risk is the metric for identifying the best route. Multiple safe zones (target cells) are supported.

![risk-nav](../img/risk-nav.png)

*Since this is a demo version, the software does not include all the aspects necessary for it to run on a mobile app*

For more detail refer to:

O’Reilly, G. J., D. Shahnazaryan, P. Dubini, E. Brunesi, A. Rosti, F. Dacarro, A. Gotti, D. Silvestri, S. Mascetti, M. Ducci, M. Ciucci, and A. Marino. 2023. **“Risk-aware navigation in industrial plants at risk of NaTech accidents**.” Int. *J. Disaster Risk Reduct.*, 88: 103620. https://doi.org/10.1016/j.ijdrr.2023.103620.


### Grid
Available sample files in **maps/**

    {
        'rows': int,
        'columns': int,
        'safe_zones': List[int],
        'cells': List[
            {
                'id': int,
                'connections': List[int],
            },
            {}, ...
        ]

        'scene_name': Optional[str],
        'map_name': Optional[str],
        'orientation_respect_north_0_360_degrees': Optional[float],
        'millimeter_per_pixel': Optional[float],
        'cell_size_cm': Optional[float],
        'cell_size_pixel': Optional[float],
    }

- rows = number of rows in a grid
- columns = number of columns in a grid
- safe_zones = IDs of destination cells
- cells - all cells
- id - unique identifier of a cell (ID), starts from 0
    - sequential from left to right, top to bottom
- connections - successor cell IDs of a cell with 'id'

### Step-by-step
Within the scope of this work, 'f' stands for 'risk'.

1. Initialize a risk array of zeros with length of number of grid cells
    a. The risk array is ideally constantly monitored for any live changes from sensors and risk (RIE) module, which is not implemented in the current demo (part of it available through src/)
2. Initialize OPEN list containing the the starting node only
    a. set node RISK to 0 irrelevant of actual risk
3. Initialize empty CLOSED list
4. While OPEN list is not empty
    a. find node with lowest RISK on the OPEN list (node i)
        i. If the node is in our destination, then **path is found**, return
    b. pop found node i from list and generate all its available successor's and set their parents to node i ('connections')
    c. put node i into the CLOSED list
    d. for each successor
        i. get the RISK value
        ii. if a node with the same position as the successor is in the OPEN, which has lower RISK than the successor, skip this successor
        iii. If a node with the same position as the successor is in the CLOSED, which has a lower RISK than the successor, skip this successor
        iv. Otherwise, add the node to the OPEN

