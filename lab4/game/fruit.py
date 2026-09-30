import math


class Fruit:
    def __init__(self, x, y, vx, vy, gravity, radius=28, kind="fruit"):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.gravity = float(gravity)
        self.radius = int(radius)
        self.kind = kind  # "fruit" or "bomb"
        self.sliced = False
        self.color = (255, 255, 255)

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

    def contains_point(self, x, y):
        return math.hypot(self.x - x, self.y - y) <= self.radius

    def segment_intersects(self, start, end, padding=0):
        """Check whether a blade segment crosses this fruit.

        A single-point collision test can miss fast mouse swipes because the
        mouse may move from one side of a fruit to the other between events.
        This method tests the shortest distance from the fruit center to the
        complete line segment instead.
        """
        if start is None:
            return self.contains_point(*end)

        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            return self.contains_point(x2, y2)

        fx = self.x - x1
        fy = self.y - y1
        segment_len_sq = dx * dx + dy * dy

        # Projection of the fruit center onto the blade segment.
        t = (fx * dx + fy * dy) / segment_len_sq
        t = max(0.0, min(1.0, t))

        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        hit_radius = self.radius + padding
        return math.hypot(self.x - closest_x, self.y - closest_y) <= hit_radius

    def off_screen(self, height):
        return self.y - self.radius > height
