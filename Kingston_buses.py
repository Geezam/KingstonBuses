from flask import Flask, render_template, jsonify
from shapely.geometry import LineString, Point
import datetime

# UPDATED: We tell Flask that your static files (images) are in a folder named 'img'
# and they should be accessible via the URL '/img/filename'
app = Flask(__name__, static_folder='img', static_url_path='/img')

# --- 1. DEFINE THE METRO MAP DATA ---
# UPDATED: Grid is now X (0-870), Y (0-610)
ROUTES = {
    "Route 21": {
        "color": "#FF6347", # Tomato Red
        "width": 8,
        "stops": {
            "Half Way Tree": (650, 100),
            "Washington Blvd": (450, 100),
            "Mandela Hwy": (250, 300), 
            "Spanish Town": (100, 500)
        },
        "duration_minutes": 2 
    },
    "Route 3": {
        "color": "#1E90FF", # Dodger Blue
        "width": 8,
        "stops": {
            "Downtown": (700, 400),
            "Marcus Garvey Dr": (550, 400),
            "Portmore Toll": (350, 400),
            "Christian Gardens": (100, 400)
        },
        "duration_minutes": 3
    }
}

# Pre-calculate the geometric lines for Shapely
ROUTE_GEOMETRIES = {}
for route_name, data in ROUTES.items():
    coords = list(data["stops"].values())
    line = LineString(coords)
    ROUTE_GEOMETRIES[route_name] = line


# --- 2. HELPER FUNCTION: WHERE IS THE BUS? ---
def get_bus_location(route_name):
    """
    Returns the current (x, y) pixel coordinates of the bus
    based on the current time.
    """
    route_line = ROUTE_GEOMETRIES[route_name]
    duration_min = ROUTES[route_name]["duration_minutes"]
    
    # Time Math: Calculate progress (0.0 to 1.0)
    now = datetime.datetime.now()
    
    # 1. Calculate total seconds for ONE WAY
    one_way_seconds = duration_min * 60
    
    # 2. Calculate total seconds for ROUND TRIP (There and Back)
    round_trip_seconds = one_way_seconds * 2
    
    # 3. Get current second in the day
    current_seconds = (now.minute * 60 + now.second + now.microsecond / 1_000_000)
    
    # 4. Find where we are in the round trip cycle
    cycle_position = current_seconds % round_trip_seconds
    
    # 5. Logic: Are we going forward or backward?
    if cycle_position <= one_way_seconds:
        # Phase 1: Going Forward (0% to 100%)
        progress = cycle_position / one_way_seconds
    else:
        # Phase 2: Going Backward (100% to 0%)
        # Calculate how far into the return trip we are
        return_time = cycle_position - one_way_seconds
        # Invert the progress so it moves backwards
        progress = 1.0 - (return_time / one_way_seconds)
    
    # Geometric Math: Find the point at that percentage
    distance_pixels = route_line.length * progress
    point = route_line.interpolate(distance_pixels)
    
    return {"x": point.x, "y": point.y}

# --- 3. FLASK ROUTES ---

@app.route('/')
def index():
    # Pass the static route data to the HTML to draw the map lines/stops
    return render_template('index.html', routes=ROUTES)

@app.route('/api/bus_positions')
def bus_positions():
    # This API is called by JavaScript every second to get updates
    positions = {}
    for route_name in ROUTES:
        positions[route_name] = get_bus_location(route_name)
    return jsonify(positions)

if __name__ == '__main__':
    app.run(debug=True)