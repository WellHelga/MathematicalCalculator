import math
from tkinter import Canvas
from calculator import calculator_expr

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None


class Graph:

    COLOR_GRAPH = "#551A8B"
    COLOR_GRID = "#D9D9D9"
    COLOR_AXIS = "#333333"

    def __init__(self, canvas: Canvas, width: int = 780, height: int = 500):
        self.canvas = canvas
        self.width = width
        self.height = height

        self.x_min, self.x_max = -10.0, 10.0
        self.y_min, self.y_max = -10.0, 10.0

    def set_range(self, x_min, x_max, y_min, y_max):
        self.x_min, self.x_max = x_min, x_max
        self.y_min, self.y_max = y_min, y_max

    def zoom(self, factor: float):
        x_center = (self.x_min + self.x_max) / 2
        y_center = (self.y_min + self.y_max) / 2

        x_range = (self.x_max - self.x_min) * factor / 2
        y_range = (self.y_max - self.y_min) * factor / 2

        self.x_min = x_center - x_range
        self.x_max = x_center + x_range
        self.y_min = y_center - y_range
        self.y_max = y_center + y_range

    def pan(self, dx_pixels: float, dy_pixels: float):
        math_width = self.x_max - self.x_min
        math_height = self.y_max - self.y_min

        dx_math = -dx_pixels / self.width * math_width
        dy_math = dy_pixels / self.height * math_height

        self.x_min += dx_math
        self.x_max += dx_math
        self.y_min += dy_math
        self.y_max += dy_math

    def clear(self):
        if self.canvas:
            self.canvas.delete("all")

    def draw(self, expr: str, mode: str = "x"):
        self.clear()
        self.draw_grid_and_labels()
        self.draw_curve(expr, mode)

    def save(self, filename: str, expr: str, mode: str = "x") -> bool:
        if Image is None:
            return False

        try:
            img = Image.new("RGB", (self.width, self.height), "white")
            draw = ImageDraw.Draw(img)

            self.draw_grid_pil(draw)

            cx = int(self.pixel_x(0))
            cy = int(self.pixel_y(0))
            if 0 <= cy <= self.height:
                draw.line([(0, cy), (self.width, cy)], fill=self.COLOR_AXIS, width=2)
            if 0 <= cx <= self.width:
                draw.line([(cx, 0), (cx, self.height)], fill=self.COLOR_AXIS, width=2)

            self.draw_curve_pil(draw, expr, mode)

            img.save(filename)
            return True
        except Exception:
            return False


    def pixel_x(self, x: float) -> float:
        return (x - self.x_min) / (self.x_max - self.x_min) * self.width

    def pixel_y(self, y: float) -> float:
        return self.height - (y - self.y_min) / (self.y_max - self.y_min) * self.height

    def get_nice_step(self, range_val: float) -> float:
        if range_val <= 0:
            return 1
        rough_step = range_val / 10
        magnitude = 10 ** math.floor(math.log10(rough_step))
        residual = rough_step / magnitude
        if residual <= 1.5:
            return magnitude
        if residual <= 3.5:
            return 2 * magnitude
        if residual <= 7.5:
            return 5 * magnitude
        return 10 * magnitude

    def draw_grid_and_labels(self):
        x_range = self.x_max - self.x_min
        y_range = self.y_max - self.y_min
        x_step = self.get_nice_step(x_range)
        y_step = self.get_nice_step(y_range)

        x = math.ceil(self.x_min / x_step) * x_step
        while x <= self.x_max:
            px = self.pixel_x(x)
            self.canvas.create_line(px, 0, px, self.height, fill=self.COLOR_GRID, width=1)
            if abs(x) > 1e-9:
                cy = self.pixel_y(0)
                self.canvas.create_line(px, cy - 4, px, cy + 4, fill=self.COLOR_AXIS, width=2)
                self.canvas.create_text(px, cy + 12, text=f"{x:g}", fill=self.COLOR_AXIS, font=("Arial", 8))
            x += x_step

        y = math.ceil(self.y_min / y_step) * y_step
        while y <= self.y_max:
            py = self.pixel_y(y)
            self.canvas.create_line(0, py, self.width, py, fill=self.COLOR_GRID, width=1)
            if abs(y) > 1e-9:
                cx = self.pixel_x(0)
                self.canvas.create_line(cx - 4, py, cx + 4, py, fill=self.COLOR_AXIS, width=2)
                self.canvas.create_text(cx - 12, py, text=f"{y:g}", fill=self.COLOR_AXIS, font=("Arial", 8))
            y += y_step

        cx = self.pixel_x(0)
        cy = self.pixel_y(0)
        if 0 <= cy <= self.height:
            self.canvas.create_line(0, cy, self.width, cy, fill=self.COLOR_AXIS, width=2)
        if 0 <= cx <= self.width:
            self.canvas.create_line(cx, 0, cx, self.height, fill=self.COLOR_AXIS, width=2)
        if 0 <= cx <= self.width and 0 <= cy <= self.height:
            self.canvas.create_text(cx - 10, cy + 12, text="0", fill=self.COLOR_AXIS, font=("Arial", 8))

    def draw_curve(self, expr: str, mode: str = "x"):
        prev_point = None

        if mode == "x":
            step = (self.x_max - self.x_min) / 500
            for i in range(501):
                x = self.x_min + i * step
                try:
                    y = calculator_expr(expr, x_value=x)
                    px = self.pixel_x(x)
                    py = self.pixel_y(y)
                    if prev_point and abs(py - prev_point[1]) < self.height:
                        self.canvas.create_line(prev_point[0], prev_point[1], px, py, fill=self.COLOR_GRAPH, width=2)
                    prev_point = (px, py)
                except:
                    prev_point = None
        else:
            step = (self.y_max - self.y_min) / 500
            for i in range(501):
                y = self.y_min + i * step
                try:
                    x = calculator_expr(expr, y_value=y)
                    px = self.pixel_x(x)
                    py = self.pixel_y(y)
                    if prev_point and abs(px - prev_point[0]) < self.width:
                        self.canvas.create_line(prev_point[0], prev_point[1], px, py, fill=self.COLOR_GRAPH, width=2)
                    prev_point = (px, py)
                except:
                    prev_point = None

    def draw_grid_pil(self, draw):
        x_range = self.x_max - self.x_min
        y_range = self.y_max - self.y_min
        x_step = self.get_nice_step(x_range)
        y_step = self.get_nice_step(y_range)

        x = math.ceil(self.x_min / x_step) * x_step
        while x <= self.x_max:
            px = int(self.pixel_x(x))
            draw.line([(px, 0), (px, self.height)], fill=self.COLOR_GRID, width=1)
            x += x_step

        y = math.ceil(self.y_min / y_step) * y_step
        while y <= self.y_max:
            py = int(self.pixel_y(y))
            draw.line([(0, py), (self.width, py)], fill=self.COLOR_GRID, width=1)
            y += y_step

    def draw_curve_pil(self, draw, expr: str, mode: str = "x"):
        prev_point = None

        if mode == "x":
            step = (self.x_max - self.x_min) / 500
            for i in range(501):
                x = self.x_min + i * step
                try:
                    y = calculator_expr(expr, x_value=x)
                    px = int(self.pixel_x(x))
                    py = int(self.pixel_y(y))
                    if prev_point and abs(py - prev_point[1]) < self.height:
                        draw.line([prev_point, (px, py)], fill=self.COLOR_GRAPH, width=2)
                    prev_point = (px, py)
                except:
                    prev_point = None
        else:
            step = (self.y_max - self.y_min) / 500
            for i in range(501):
                y = self.y_min + i * step
                try:
                    x = calculator_expr(expr, y_value=y)
                    px = int(self.pixel_x(x))
                    py = int(self.pixel_y(y))
                    if prev_point and abs(px - prev_point[0]) < self.width:
                        draw.line([prev_point, (px, py)], fill=self.COLOR_GRAPH, width=2)
                    prev_point = (px, py)
                except:
                    prev_point = None