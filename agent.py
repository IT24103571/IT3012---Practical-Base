# agent.py
from collections import deque
import heapq
import random
import math
from turtle import pos
from logic_engine import KnowledgeBase

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)



class SimpleReflexAgent:

    def sense_and_act(self, percept):

        # IF food is ahead
        # THEN move forward
        if percept['food_here']:

            return 'Right'

        # IF wall is ahead
        # THEN turn left
        elif percept['wall_ahead']:

            return 'Up'

        # ELSE move forward
        else:

            return 'Right'


class ModelBasedAgent:

    def __init__(self):

        # -------------------------------------------------
        # INTERNAL MEMORY
        # -------------------------------------------------

        # Remember cells that have been visited
        self.visited_cells = set()

        # Remember cells where movement was blocked
        self.blocked_cells = set()

        # -------------------------------------------------
        # INTERNAL MODEL OF POSITION
        # -------------------------------------------------

        self.x = 0
        self.y = 0

        # Current direction
        self.facing = 'Right'

        # Remember previous action
        self.last_action = None

    # =====================================================
    # FIND NEXT CELL
    # =====================================================

    def get_next_position(self, direction):

        if direction == 'Up':

            return (
                self.x,
                self.y + 1
            )

        elif direction == 'Down':

            return (
                self.x,
                self.y - 1
            )

        elif direction == 'Left':

            return (
                self.x - 1,
                self.y
            )

        else:

            return (
                self.x + 1,
                self.y
            )

    # =====================================================
    # FIND LEFT DIRECTION
    # =====================================================

    def get_left_direction(self):

        if self.facing == 'Up':
            return 'Left'

        elif self.facing == 'Left':
            return 'Down'

        elif self.facing == 'Down':
            return 'Right'

        else:
            return 'Up'

    # =====================================================
    # FIND RIGHT DIRECTION
    # =====================================================

    def get_right_direction(self):

        if self.facing == 'Up':
            return 'Right'

        elif self.facing == 'Right':
            return 'Down'

        elif self.facing == 'Down':
            return 'Left'

        else:
            return 'Up'

    # =====================================================
    # FIND BACKWARD DIRECTION
    # =====================================================

    def get_back_direction(self):

        if self.facing == 'Up':
            return 'Down'

        elif self.facing == 'Down':
            return 'Up'

        elif self.facing == 'Left':
            return 'Right'

        else:
            return 'Left'

    # =====================================================
    # SENSE AND ACT
    # =====================================================

    def sense_and_act(self, percept):

        # -------------------------------------------------
        # 1. Record current cell in memory
        # -------------------------------------------------

        current_cell = (
            self.x,
            self.y
        )

        self.visited_cells.add(current_cell)

        # -------------------------------------------------
        # 2. IF food is ahead
        # THEN move forward
        # -------------------------------------------------

        if percept['food_here']:

            action = self.facing

        # -------------------------------------------------
        # 3. IF wall is ahead
        # THEN choose another direction
        # -------------------------------------------------

        elif percept['wall_ahead']:

            directions = [
                self.get_left_direction(),
                self.get_right_direction(),
                self.get_back_direction()
            ]

            action = None

            # First try an unvisited cell
            for direction in directions:

                next_cell = self.get_next_position(
                    direction
                )

                if (
                    next_cell not in self.visited_cells
                    and next_cell not in self.blocked_cells
                ):

                    action = direction
                    break

            # If all are visited, try any non-blocked cell
            if action is None:

                for direction in directions:

                    next_cell = self.get_next_position(
                        direction
                    )

                    if next_cell not in self.blocked_cells:

                        action = direction
                        break

            # Last fallback
            if action is None:

                action = self.get_back_direction()

        # -------------------------------------------------
        # 4. No wall ahead
        # -------------------------------------------------

        else:

            # Check forward cell
            forward_cell = self.get_next_position(
                self.facing
            )

            # If forward is new, keep moving forward
            if (
                forward_cell not in self.visited_cells
                and forward_cell not in self.blocked_cells
            ):

                action = self.facing

            else:

                # We have already visited this cell.
                # Try another direction.
                directions = [
                    self.get_left_direction(),
                    self.get_right_direction(),
                    self.get_back_direction()
                ]

                action = None

                # Prefer unvisited cells
                for direction in directions:

                    next_cell = self.get_next_position(
                        direction
                    )

                    if (
                        next_cell not in self.visited_cells
                        and next_cell not in self.blocked_cells
                    ):

                        action = direction
                        break

                # If no unvisited cell exists,
                # try any non-blocked direction.
                if action is None:

                    for direction in directions:

                        next_cell = self.get_next_position(
                            direction
                        )

                        if next_cell not in self.blocked_cells:

                            action = direction
                            break

                # Final fallback
                if action is None:

                    action = self.facing

        # Remember the selected action
        self.last_action = action

        return action

    # =====================================================
    # UPDATE INTERNAL MODEL
    # =====================================================

    def update_position(
        self,
        action,
        movement_successful
    ):

        # The direction changes to the selected action
        self.facing = action

        # Find the cell we attempted to enter
        target = self.get_next_position(action)

        # -------------------------------------------------
        # Movement succeeded
        # -------------------------------------------------

        if movement_successful:

            # The agent really moved,
            # so update its internal position.

            self.x, self.y = target

        # -------------------------------------------------
        # Movement failed
        # -------------------------------------------------

        else:

            # The agent could not enter this cell.
            # Remember it as blocked.

            self.blocked_cells.add(target)

class SearchAgent:

    def __init__(self):
        self.plan = []
        self.active_algo = 'AStar'
        self.kb = KnowledgeBase()

        self.kb.tell_rule(
            ["TargetVisible", "HasDust"],
            "SafeToEngage"
        )

        self.kb.tell_rule(
            ["SafeToEngage", "BloodseekerMissing"],
            "Retreat"
        )

    def bfs_search(self, start, goal, grid_size, walls):
        frontier = deque()
        frontier.append((start, []))

        reached = {start}

        while frontier:
            current, path = frontier.popleft()

            if current == goal:
                return path

            x, y = current

            neighbors = [
                ((x, y + 1), 'Up'),
                ((x, y - 1), 'Down'),
                ((x - 1, y), 'Left'),
                ((x + 1, y), 'Right')
            ]

            for next_state, action in neighbors:
                if (
                    0 <= next_state[0] < grid_size[0]
                    and 0 <= next_state[1] < grid_size[1]
                    and next_state not in walls
                    and next_state not in reached
                ):
                    reached.add(next_state)
                    frontier.append(
                        (next_state, path + [action])
                    )

        return None

    def dfs_search(self, start, goal, grid_size, walls):
        frontier = []
        frontier.append((start, []))

        reached = {start}

        while frontier:
            current, path = frontier.pop()

            if current == goal:
                return path

            x, y = current

            neighbors = [
                ((x, y + 1), 'Up'),
                ((x, y - 1), 'Down'),
                ((x - 1, y), 'Left'),
                ((x + 1, y), 'Right')
            ]

            for next_state, action in neighbors:
                if (
                    0 <= next_state[0] < grid_size[0]
                    and 0 <= next_state[1] < grid_size[1]
                    and next_state not in walls
                    and next_state not in reached
                ):
                    reached.add(next_state)
                    frontier.append(
                        (next_state, path + [action])
                    )

        return None

    def ucs_search(self, start, goal, grid_size, walls):
        frontier = []
        heapq.heappush(
            frontier,
            (0, start, [])
        )

        reached = {start: 0}

        while frontier:
            cost, current, path = heapq.heappop(frontier)

            if current == goal:
                return path

            x, y = current

            neighbors = [
                ((x, y + 1), 'Up'),
                ((x, y - 1), 'Down'),
                ((x - 1, y), 'Left'),
                ((x + 1, y), 'Right')
            ]

            for next_state, action in neighbors:

                if (
                    0 <= next_state[0] < grid_size[0]
                    and 0 <= next_state[1] < grid_size[1]
                    and next_state not in walls
                ):
                    new_cost = cost + 1

                    if (
                        next_state not in reached
                        or new_cost < reached[next_state]
                    ):
                        reached[next_state] = new_cost

                        heapq.heappush(
                            frontier,
                            (
                                new_cost,
                                next_state,
                                path + [action]
                            )
                        )

    def sense_and_act(self, percept):

        # If there is no current plan, create a new one
        if not self.plan:

            start = percept['agent_pos']
            all_food = percept['all_food']
            grid_size = percept['grid_size']
            walls = set(percept['walls'])

            # If there is no food left
            if not all_food:
                return 'Stay'

            # Find the closest food using Manhattan distance
            goal = min(
                all_food,
                key=lambda food:
                    abs(start[0] - food[0]) +
                    abs(start[1] - food[1])
            )

            # Choose the search algorithm
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'AStar':
                self.plan = self.astar_search(
                    start,
                    goal,
                    walls,
                    grid_size,
                    'manhattan'
    )
    
            # If no path was found
            if not self.plan:
                return 'Stay'

        # Execute the first action in the plan
        return self.plan.pop(0)

    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        return math.sqrt(
            (pos[0] - goal[0]) ** 2 +
            (pos[1] - goal[1]) ** 2
    )

    
def astar_search(
    self, start, goal, walls, grid_size,
    heuristic='manhattan', tile_facts=None
):
    frontier = []
    reached_states = set()

    if tile_facts is None:
        tile_facts = {}

    # Calculate heuristic for the starting position
    if heuristic == 'manhattan':
        h_cost = self.manhattan_distance(start, goal)
    else:
        h_cost = self.euclidean_distance(start, goal)

    # Starting node has travelled 0 steps
    g_cost = 0

    # A* formula: f(n) = g(n) + h(n)
    f_cost = g_cost + h_cost

    # Add starting node to priority queue
    heapq.heappush(
        frontier,
        (f_cost, g_cost, start, [])
    )

    while frontier:

        # Get node with lowest f(n)
        f_cost, g_cost, current_pos, path_taken = heapq.heappop(
            frontier
        )

        # Check if goal is reached
        if current_pos == goal:
            return path_taken

        # Remember that this state was explored
        reached_states.add(current_pos)

        x, y = current_pos

        # Four possible movements
        neighbors = [
            ((x, y + 1), 'Up'),
            ((x, y - 1), 'Down'),
            ((x - 1, y), 'Left'),
            ((x + 1, y), 'Right')
        ]

        # Explore neighbours
        for next_pos, action in neighbors:

            if (
                0 <= next_pos[0] < grid_size[0]
                and 0 <= next_pos[1] < grid_size[1]
                and next_pos not in walls
                and next_pos not in reached_states
            ):

                # Clear facts from the previous tile
                self.kb.clear_facts()

                # Add facts for this neighbour
                for fact in tile_facts.get(next_pos, []):
                    self.kb.tell_fact(fact)

                # Apply forward chaining
                self.kb.forward_chain()

                # Skip the tile if Retreat is inferred
                if 'Retreat' in self.kb.facts:
                    continue

                # Cost of reaching the neighbour
                new_g_cost = g_cost + 1

                # Estimate distance from neighbour to goal
                if heuristic == 'manhattan':
                    new_h_cost = self.manhattan_distance(
                        next_pos, goal
                    )
                else:
                    new_h_cost = self.euclidean_distance(
                        next_pos, goal
                    )

                # A* formula
                new_f_cost = new_g_cost + new_h_cost

                # Add neighbour to priority queue
                heapq.heappush(
                    frontier,
                    (
                        new_f_cost,
                        new_g_cost,
                        next_pos,
                        path_taken + [action]
                    )
                )

    # No path found
    return None


agent = SearchAgent()

print(agent.manhattan_distance((0, 0), (3, 4)))
print(agent.euclidean_distance((0, 0), (3, 4)))
