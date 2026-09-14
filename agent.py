import random

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
