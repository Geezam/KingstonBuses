import tkinter as tk
import math
from contstants import (WINDOW_WIDTH, WINDOW_HEIGHT,
                        ROUTE_52, ROUTE_72, ROUTE_97)


class BusTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Kingston JUTC Bus Tracker")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # Create the Canvas
        self.canvas = tk.Canvas(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                                bg="white")
        self.canvas.pack()

        # Draw the Route map Background
        self.draw_map()

        # Buses initialization
        self.buses = []

        # Bus 1: Assigned to ROUTE 52
        self.add_bus(route=ROUTE_52, start_index=0, color="#9768EE", speed=1.0)

        # Bus 2: Assigned to ROUTE 72
        self.add_bus(route=ROUTE_72, start_index=0, color="#F0CE15", speed=1.5)

        # Bus 3: Assigned to ROUTE 97
        self.add_bus(route=ROUTE_97, start_index=0, color="#0896D7", speed=2.0)

        # Start the movement loop
        self.animate_buses()

    def draw_map(self):
        """Draws the background image."""
        try:
            self.bg_image = tk.PhotoImage(file="img/JUTC_partial.png")
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except Exception as e:
            print(f"Could not load image: {e}")
            print("Drawing on white background instead.")

    def add_bus(self, route, start_index, color, speed):
        """Helper to create a new bus and add it to our list."""
        # Start within valid bounds
        if start_index >= len(route) - 1:
            start_index = 0

        start_pos = route[start_index]

        # Create the visual circle for the bus
        bus_id = self.canvas.create_oval(
            start_pos["x"] - 10, start_pos["y"] - 10,
            start_pos["x"] + 10, start_pos["y"] + 10,
            fill=color, outline="white", width=2
        )

        # Create the state dictionary
        bus_data = {
            "id": bus_id,
            "route": route,
            "current_stop_index": start_index,
            "target_stop_index": start_index + 1,
            "progress": 0.0,
            "speed": speed,
            "direction": 1  # 1 = Forward, -1 = Backward
        }

        self.buses.append(bus_data)

    def animate_buses(self):
        """Calculates position for ALL buses using constant pixel speed."""

        for bus in self.buses:
            # Get route and stop info
            current_route = bus["route"]
            start_stop = current_route[bus["current_stop_index"]]
            end_stop = current_route[bus["target_stop_index"]]

            # 1. Calculate distance
            dx = end_stop["x"] - start_stop["x"]
            dy = end_stop["y"] - start_stop["y"]
            distance = math.sqrt(dx*dx + dy*dy)

            if distance == 0:
                distance = 1

            # 2. Update Progress
            percent_to_move = bus["speed"] / distance
            bus["progress"] += percent_to_move

            # 3. Clamp progress for drawing
            draw_progress = bus["progress"]
            if draw_progress > 1.0:
                draw_progress = 1.0

            # 4. Calculate Coordinates to Draw
            current_x = start_stop["x"] + (dx * draw_progress)
            current_y = start_stop["y"] + (dy * draw_progress)

            # Move visual
            self.canvas.coords(bus["id"],
                               current_x - 10, current_y - 10,
                               current_x + 10, current_y + 10)

            # 5. Check for Arrival
            if bus["progress"] >= 1.0:
                bus["progress"] = 0.0
                bus["current_stop_index"] = bus["target_stop_index"]
                bus["target_stop_index"] += bus["direction"]

                # Turn around logic
                if bus["target_stop_index"] >= len(current_route):
                    bus["direction"] = -1
                    bus["target_stop_index"] = len(current_route) - 2

                if bus["target_stop_index"] < 0:
                    bus["direction"] = 1
                    bus["target_stop_index"] = 1

        # Run again in 20ms
        self.after(20, self.animate_buses)
