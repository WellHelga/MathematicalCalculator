import tkinter as tk
from calculator import calculator_expr, find_variables
from tkinter import filedialog
from graph import Graph


class Calculator:

    COLOR_BG = "mediumpurple4"
    COLOR_BTN_BG = "white"
    COLOR_BTN_FG = "purple4"
    COLOR_TEXT = "white"

    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор математических выражений")
        self.root.geometry("800x600")
        self.root.configure(bg=self.COLOR_BG)

        self.draw_width = 780
        self.draw_height = 500

        self.drag_start_x = 0
        self.drag_start_y = 0

        self.canvas = None
        self.plotter = None

        self.create_widgets()

    def create_widgets(self):

        frame = tk.Frame(self.root, bg=self.COLOR_BG)
        frame.pack(pady=10)

        self.entry = tk.Entry(frame, width=40, font=("Arial", 14))
        self.entry.pack(side=tk.LEFT, padx=5)

        tk.Button(frame, text="Вычислить", command=self.execute, font=("Arial", 12, "bold"), bg=self.COLOR_BTN_BG, fg=self.COLOR_BTN_FG, activebackground="mediumpurple3", width=12).pack(side=tk.LEFT, padx=2)

        self.save_btn = tk.Button(frame, text="Сохранить график", command=self.save_graph, font=("Arial", 12, "bold"), bg=self.COLOR_BTN_BG, fg=self.COLOR_BTN_FG, activebackground="mediumpurple3", width=15, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=2)

        self.label = tk.Label(self.root, text="Результат:", font=("Arial", 14, "bold"), bg=self.COLOR_BG, fg=self.COLOR_TEXT)
        self.label.pack(pady=8)

        self.entry.bind("<Return>", lambda event: self.execute())

    def show_canvas(self):

        if self.canvas is None:
            self.canvas = tk.Canvas(self.root, bg="white",
                                    width=self.draw_width, height=self.draw_height,
                                    highlightbackground=self.COLOR_BG, highlightthickness=3)
            self.canvas.pack(padx=10, pady=10)

            self.plotter = Graph(self.canvas, self.draw_width, self.draw_height)

            self.canvas.bind("<MouseWheel>", self.mouse_wheel)
            self.canvas.bind("<Button-4>", self.mouse_wheel)
            self.canvas.bind("<Button-5>", self.mouse_wheel)
            self.canvas.bind("<ButtonPress-1>", self.drag_start)
            self.canvas.bind("<B1-Motion>", self.drag)

    def hide_canvas(self):

        if self.canvas is not None:
            self.canvas.destroy()
            self.canvas = None
            self.plotter = None

    def execute(self):

        expr = self.entry.get().strip()
        if not expr:
            self.show_message("Внимание", "Введите выражение")
            return

        try:
            variables = find_variables(expr)
            if not variables:
                result = calculator_expr(expr)
                self.label.config(text=f"Результат: {self.format_result(result)}")
                self.hide_canvas()
                self.save_btn.config(state=tk.DISABLED)
            else:
                has_x = "x" in variables
                has_y = "y" in variables

                if has_x and not has_y:
                    mode = "x"
                elif has_y and not has_x:
                    mode = "y"
                else:
                    self.show_message("Ошибка","График должен иметь x или y")
                    return

                self.show_canvas()
                self.plotter.draw(expr, mode)

                label_text = f"График: y = {expr}" if mode == "x" else f"График: x = {expr}"
                self.label.config(text=label_text)
                self.save_btn.config(state=tk.NORMAL)

        except Exception as e:
            self.show_message("Ошибка", str(e))

    def format_result(self, value):
        if abs(value - round(value)) < 1e-10:
            return f"{value:.1f}"
        else:
            formatted = f"{value:.10f}".rstrip("0")
            if formatted.endswith("."):
                formatted += "0"
            return formatted

    def show_message(self, title, message):

        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.configure(bg="white")

        msg_label = tk.Label(dialog, text=message, font=("Arial", 11), bg="white", fg="purple4", wraplength=250, justify="center")
        msg_label.pack(expand=True, padx=20, pady=20)

        ok_btn = tk.Button(dialog, text="OK", command=dialog.destroy, font=("Arial", 10, "bold"), bg="mediumpurple4", fg="white", width=10)
        ok_btn.pack(pady=5)

        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
        dialog.geometry(f"+{x}+{y}")
        dialog.grab_set()
        dialog.wait_window()

    def mouse_wheel(self, event):
        if event.num == 4:
            factor = 0.9
        elif event.num == 5:
            factor = 1.1
        else:
            factor = 0.9 if event.delta > 0 else 1.1

        self.plotter.zoom(factor)
        self.redraw()

    def drag_start(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.plotter.pan(dx, dy)
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.redraw()

    def redraw(self):

        if self.plotter and self.save_btn["state"] == tk.NORMAL:
            expr = self.entry.get().strip()
            variables = find_variables(expr)
            mode = "y" if ("y" in variables and "x" not in variables) else "x"
            self.plotter.draw(expr, mode)

    def save_graph(self):

        if self.plotter is None:
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG файлы", "*.png"), ("Все файлы", "*.*")]
        )
        if filename:
            expr = self.entry.get().strip()
            variables = find_variables(expr)
            mode = "y" if ("y" in variables and "x" not in variables) else "x"

            if self.plotter.save(filename, expr, mode):
                self.show_message("Успешно",f"График сохранён")
            else:
                self.show_message("Ошибка", "График не сохранен")