class Selection:
    def __init__(self, network):
        # Rectangle selection
        self.network = network
        self.is_selecting = False
        self.selection_start = None
        self.selection_end = None
        self.selected_objects = []
    
    def perform_selection(self):
        """Selects weights and neruons touching selection rectangle"""
        if not self.selection_start or not self.selection_end:
            return

        x1, y1 = self.selection_start
        x2, y2 = self.selection_end

        x_min, x_max = sorted([x1, x2])
        y_min, y_max = sorted([y1, y2])

        def line_intersects_rect(line_start, line_end, rect_x_min, rect_x_max, rect_y_min, rect_y_max):
            """Checks if line intersect the rectangle"""
            def on_segment(p, q, r):
                """Checks if point q is on point p section"""
                if min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and min(p[1], r[1]) <= q[1] <= max(p[1], r[1]):
                    return True
                return False

            def orientation(p, q, r):
                """Calculates orientation of 3 points, checking if they are colinear"""
                val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
                if val == 0:
                    return 0
                return 1 if val > 0 else 2

            def do_intersect(p1, q1, p2, q2):
                """Checks if two lines (p1, q1) and (p2, q2) intersects"""
                o1 = orientation(p1, q1, p2)
                o2 = orientation(p1, q1, q2)
                o3 = orientation(p2, q2, p1)
                o4 = orientation(p2, q2, q1)

                if o1 != o2 and o3 != o4:
                    return True  # different orientation -> intersect

                if o1 == 0 and on_segment(p1, p2, q1): return True
                if o2 == 0 and on_segment(p1, q2, q1): return True
                if o3 == 0 and on_segment(p2, p1, q2): return True
                if o4 == 0 and on_segment(p2, q1, q2): return True

                return False

            # Selection rectangle corners
            rect_corners = [
                (rect_x_min, rect_y_min), (rect_x_max, rect_y_min),
                (rect_x_max, rect_y_max), (rect_x_min, rect_y_max)
            ]

            # Checks if line intersect any side of selection rectangle 
            for i in range(4):
                if do_intersect(line_start, line_end, rect_corners[i], rect_corners[(i + 1) % 4]):
                    return True

            # Checks if line is inside selection rectangle
            if (rect_x_min <= line_start[0] <= rect_x_max and rect_y_min <= line_start[1] <= rect_y_max and
                    rect_x_min <= line_end[0] <= rect_x_max and rect_y_min <= line_end[1] <= rect_y_max):
                return True

            return False

        # Select lines
        for line in self.network.connections:
            start = (line.start.x, line.start.y)
            end = (line.end.x, line.end.y)

            if line_intersects_rect(start, end, x_min, x_max, y_min, y_max):
                line.selected = True
            else:
                line.selected = False

        # Select neurons
        for layer in self.network.neurons:
            for neuron in layer:
                if x_min <= neuron.x <= x_max and y_min <= neuron.y <= y_max:
                    neuron.selected = True
                else:
                    neuron.selected = False