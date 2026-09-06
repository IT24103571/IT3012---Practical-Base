# visual_grid_game.py

import random
import tkinter as tk


# =========================================================
# ENVIRONMENT
# =========================================================

class VisualGridHuntGame:
    """Pacman-style grid environment."""

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=2,
        custom_walls=None,
        num_traps=5
    ):
        self.width = width
        self.height = height

        # Starting position
        self.agent_pos = [0, 0]

        # Initial direction
        self.facing = 'Right'

        # -------------------------------------------------
        # Walls
        # -------------------------------------------------

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7)
            }

        # -------------------------------------------------
        # Food
        # -------------------------------------------------

        self.food_positions = set()

        while len(self.food_positions) < num_food:

            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)

            pos_tuple = (fx, fy)

            if (
                pos_tuple != (0, 0)
                and pos_tuple not in self.walls
            ):
                self.food_positions.add(pos_tuple)

        # -------------------------------------------------
        # Toxic traps
        # -------------------------------------------------

        self.toxic_traps = set()

        while len(self.toxic_traps) < num_traps:

            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)

            trap_pos = (tx, ty)

            if (
                trap_pos != (0, 0)
                and trap_pos not in self.walls
                and trap_pos not in self.food_positions
            ):
                self.toxic_traps.add(trap_pos)

        # -------------------------------------------------
        # Opponents
        # -------------------------------------------------

        self.opponents = []

        while len(self.opponents) < num_opponents:

            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)

            op_pos = [ox, oy]

            if (
                tuple(op_pos) != (0, 0)
                and tuple(op_pos) not in self.walls
                and tuple(op_pos) not in self.food_positions
            ):
                self.opponents.append(op_pos)

        # -------------------------------------------------
        # Game state
        # -------------------------------------------------

        self.score = 0
        self.steps = 0
        self.collision = False

    # =====================================================
    # SENSOR
    # =====================================================

    def get_percept(self) -> dict:

        x, y = self.agent_pos

        # Find the cell directly in front
        if self.facing == 'Up':
            front = (x, y + 1)

        elif self.facing == 'Down':
            front = (x, y - 1)

        elif self.facing == 'Left':
            front = (x - 1, y)

        else:
            front = (x + 1, y)

        # A grid boundary is also treated as a wall
        wall_ahead = (
            front in self.walls
            or front[0] < 0
            or front[0] >= self.width
            or front[1] < 0
            or front[1] >= self.height
        )

        return {
            'wall_ahead': wall_ahead,
            'food_here': front in self.food_positions
        }

    # =====================================================
    # EXECUTE ACTION
    # =====================================================

    def execute_action(self, action: str):

        self.steps += 1

        new_pos = list(self.agent_pos)

        # -------------------------------------------------
        # Decide movement
        # -------------------------------------------------

        if action == 'Up':

            self.facing = 'Up'
            new_pos[1] += 1

        elif action == 'Down':

            self.facing = 'Down'
            new_pos[1] -= 1

        elif action == 'Left':

            self.facing = 'Left'
            new_pos[0] -= 1

        elif action == 'Right':

            self.facing = 'Right'
            new_pos[0] += 1

        # -------------------------------------------------
        # Check whether movement is possible
        # -------------------------------------------------

        if (
            new_pos[0] < 0
            or new_pos[0] >= self.width
            or new_pos[1] < 0
            or new_pos[1] >= self.height
            or tuple(new_pos) in self.walls
        ):

            # Movement failed
            self.score -= 5

            return False

        # Movement succeeded
        self.agent_pos = new_pos

        # -------------------------------------------------
        # Check food
        # -------------------------------------------------

        tuple_pos = tuple(self.agent_pos)

        if tuple_pos in self.food_positions:

            self.food_positions.remove(tuple_pos)
            self.score += 20

        # -------------------------------------------------
        # Check toxic trap
        # -------------------------------------------------

        if tuple_pos in self.toxic_traps:

            self.score -= 15

        # -------------------------------------------------
        # Move opponents
        # -------------------------------------------------

        for op in self.opponents:

            move = random.choice([
                'Up',
                'Down',
                'Left',
                'Right',
                'Stay'
            ])

            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1

            elif move == 'Down' and op[1] > 0:
                op[1] -= 1

            elif move == 'Left' and op[0] > 0:
                op[0] -= 1

            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:

                self.score -= 50
                self.collision = True

        return True

    # =====================================================
    # CHECK IF GAME IS FINISHED
    # =====================================================

    def is_done(self) -> bool:

        return (
            len(self.food_positions) == 0
            or self.steps >= 100
            or self.collision
        )


# =========================================================
# STEP 1.2 - SIMPLE REFLEX AGENT
# =========================================================

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


# =========================================================
# STEP 1.3 - MODEL-BASED AGENT
# =========================================================

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


# =========================================================
# GUI
# =========================================================

class GridGameGUI:

    def __init__(
        self,
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0,
        walls=None
    ):

        self.root = root

        self.root.title(
            "IT3012 - Model-Based Agent"
        )

        # -------------------------------------------------
        # Create environment
        # -------------------------------------------------

        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls
        )

        # -------------------------------------------------
        # Create Model-Based Agent
        # -------------------------------------------------

        self.agent = ModelBasedAgent()

        # -------------------------------------------------
        # Canvas
        # -------------------------------------------------

        max_canvas_dim = 600

        self.cell_size = max(
            20,
            min(
                max_canvas_dim // self.env.width,
                max_canvas_dim // self.env.height
            )
        )

        canvas_w = (
            self.env.width
            * self.cell_size
        )

        canvas_h = (
            self.env.height
            * self.cell_size
        )

        self.canvas = tk.Canvas(
            root,
            width=canvas_w,
            height=canvas_h,
            bg="white"
        )

        self.canvas.pack()

        # -------------------------------------------------
        # Information label
        # -------------------------------------------------

        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0",
            font=("Arial", 14)
        )

        self.label.pack(pady=10)

        # -------------------------------------------------
        # Start button
        # -------------------------------------------------

        self.btn = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop,
            font=("Arial", 12),
            bg="#000066",
            fg="white"
        )

        self.btn.pack(pady=5)

        self.draw_grid()

    # =====================================================
    # DRAW GRID
    # =====================================================

    def draw_grid(self):

        self.canvas.delete("all")

        # -------------------------------------------------
        # Draw grid and walls
        # -------------------------------------------------

        for x in range(self.env.width):

            for y in range(self.env.height):

                x1 = (
                    x
                    * self.cell_size
                )

                y1 = (
                    self.env.height
                    - 1
                    - y
                ) * self.cell_size

                x2 = (
                    x1
                    + self.cell_size
                )

                y2 = (
                    y1
                    + self.cell_size
                )

                color = (
                    "#f1f5f9"
                    if (x, y)
                    not in self.env.walls
                    else "#64748b"
                )

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline="#cbd5e1"
                )

                # Draw W on walls
                if (
                    self.cell_size >= 40
                    and (x, y) in self.env.walls
                ):

                    self.canvas.create_text(
                        x1 + self.cell_size / 2,
                        y1 + self.cell_size / 2,
                        text="W",
                        fill="white",
                        font=("Arial", 8, "bold")
                    )

        # -------------------------------------------------
        # Draw food
        # -------------------------------------------------

        for fx, fy in self.env.food_positions:

            offset = (
                self.cell_size
                * 0.25
            )

            x1 = (
                fx
                * self.cell_size
                + offset
            )

            y1 = (
                (
                    self.env.height
                    - 1
                    - fy
                )
                * self.cell_size
                + offset
            )

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                fill="#f59e0b",
                outline="#d97706"
            )

        # -------------------------------------------------
        # Draw toxic traps
        # -------------------------------------------------

        for tx, ty in self.env.toxic_traps:

            offset = (
                self.cell_size
                * 0.25
            )

            x1 = (
                tx
                * self.cell_size
                + offset
            )

            y1 = (
                (
                    self.env.height
                    - 1
                    - ty
                )
                * self.cell_size
                + offset
            )

            self.canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                fill="purple",
                outline="darkviolet"
            )

        # -------------------------------------------------
        # Draw opponents
        # -------------------------------------------------

        for ox, oy in self.env.opponents:

            offset = (
                self.cell_size
                * 0.2
            )

            x1 = (
                ox
                * self.cell_size
                + offset
            )

            y1 = (
                (
                    self.env.height
                    - 1
                    - oy
                )
                * self.cell_size
                + offset
            )

            self.canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="#990000",
                outline="#7a0000"
            )

        # -------------------------------------------------
        # Draw agent
        # -------------------------------------------------

        ax, ay = self.env.agent_pos

        offset = (
            self.cell_size
            * 0.15
        )

        x1 = (
            ax
            * self.cell_size
            + offset
        )

        y1 = (
            (
                self.env.height
                - 1
                - ay
            )
            * self.cell_size
            + offset
        )

        self.canvas.create_oval(
            x1,
            y1,
            x1 + self.cell_size * 0.7,
            y1 + self.cell_size * 0.7,
            fill="#000066",
            outline="#1e3a8a"
        )

    # =====================================================
    # RUN SIMULATION
    # =====================================================

    def run_loop(self):

        self.btn.config(
            state="disabled"
        )

        def step():

            if not self.env.is_done():

                # -----------------------------------------
                # 1. Get percept
                # -----------------------------------------

                percept = (
                    self.env.get_percept()
                )

                # -----------------------------------------
                # 2. Agent chooses action
                # -----------------------------------------

                action = (
                    self.agent.sense_and_act(
                        percept
                    )
                )

                # -----------------------------------------
                # 3. Environment executes action
                # -----------------------------------------

                movement_successful = (
                    self.env.execute_action(
                        action
                    )
                )

                # -----------------------------------------
                # 4. Update agent's internal model
                # -----------------------------------------

                self.agent.update_position(
                    action,
                    movement_successful
                )

                # -----------------------------------------
                # 5. Redraw
                # -----------------------------------------

                self.draw_grid()

                self.label.config(
                    text=(
                        f"Score: {self.env.score} | "
                        f"Steps: {self.env.steps} | "
                        f"Action: {action}"
                    )
                )

                self.root.after(
                    250,
                    step
                )

            else:

                if self.env.collision:

                    end_text = (
                        f"Collision! Game Over! "
                        f"Final Score: "
                        f"{self.env.score}"
                    )

                else:

                    end_text = (
                        f"Finished! "
                        f"Final Score: "
                        f"{self.env.score}"
                    )

                self.label.config(
                    text=end_text
                )

                self.btn.config(
                    state="normal"
                )

        step()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0
    )

    root.mainloop()
