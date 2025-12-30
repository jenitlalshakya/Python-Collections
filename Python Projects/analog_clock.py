import tkinter as tk
import math
import time

# --- Config ---
SIZE = 400
RADIUS = SIZE // 2 - 20
CENTER = (SIZE // 2, SIZE // 2)
UPDATE_MS = 100

# Hand lengths (fraction of RADIUS)
HOUR_LEN = 0.5
MIN_LEN = 0.75
SEC_LEN = 0.9

#Hand widths
HOUR_W = 6
MIN_W = 4
SEC_W = 2

# Color
BG_COLOR = "white"
FACE_COLOR = "white"
BORDER_COLOR = "#222"
HOUR_COLOR = "#222"
MIN_COLOR = "#222"
SEC_COLOR = "#c33"


# --- Helper functions ---
def polar_to_cart(cx, cy, radius, angle_deg):
    """Convert polar coords (angle in degrees, 0 at 12 o'clock) to canvas coords."""
    angle_rad = math.radians(angle_deg - 90)
    x = cx + radius * math.cos(angle_rad)
    y = cy + radius * math.sin(angle_rad)
    return x, y


def time_to_angles(now=None):
    """Return (hour_angle, minute_angle, second_angle) in degrees."""
    if now is None:
        now = time.localtime()
        frac_sec = time.time() - int(time.time())
    else:
        frac_sec = 0.0

    h = now.tm_hour % 12
    m = now.tm_min
    s = now.tm_sec + frac_sec

    sec_angle = (s / 60.0) * 360.0
    min_angle = (m / 60.0) * 360.0 + (s / 60.0) * 6.0
    hour_angle = (h / 12.0) * 360.0 + (m / 60.0) * 30.0 + (s / 3600.0) * 30.0
    return hour_angle, min_angle, sec_angle


# --- Main App ---
class AnalogClock(tk.Tk):
    def __init__(self, size=SIZE):
        super().__init__()
        self.title("Analog Clock")
        self.resizable(False, False)

        self.size = size
        self.radius = size // 2 - 20
        self.cx, self.cy = size // 2, size // 2

        self.canvas = tk.Canvas(self, width=size, height=size, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()

        self.draw_face()
        self.hour_hand = self.canvas.create_line(0,0,0,0, width=HOUR_W, capstyle=tk.ROUND)
        self.min_hand = self.canvas.create_line(0,0,0,0, width=MIN_W,capstyle=tk.ROUND)
        self.sec_hand = self.canvas.create_line(0,0,0,0, width=SEC_W, capstyle=tk.ROUND)

        self.center_dot = self.canvas.create_oval(
            self.cx-6, self.cy-6, self.cx+6, self.cy+6, fill=BORDER_COLOR, outline=BORDER_COLOR)

        self.update_clock()


    def draw_face(self):
        self.canvas.create_oval(self.cx-self.radius-6, self.cy-self.radius-6,
                                self.cx+self.radius+6, self.cy+self.radius+6,
                                fill=BORDER_COLOR, outline="")
        self.canvas.create_oval(self.cx-self.radius, self.cy-self.radius,
                                self.cx+self.radius, self.cy+self.radius,
                                fill=FACE_COLOR, outline="")

        for hour in range(1, 13):
            angle = (hour / 12.0) * 360.0
            x_outer, y_outer = polar_to_cart(self.cx, self.cy, self.radius - 6, angle)
            if hour % 3 == 0:
                inner_r = self.radius - 30
            else:
                inner_r = self.radius - 20
            x_inner, y_inner = polar_to_cart(self.cx, self.cy, inner_r, angle)
            self.canvas.create_line(x_inner, y_inner, x_outer, y_outer, width=2)

            # numbers slightly inside the inner tick
            num_r = self.radius - 50
            x_num, y_num = polar_to_cart(self.cx, self.cy, num_r, angle)
            self.canvas.create_text(x_num, y_num, text=str(hour), font=("Helvetica", int(self.size*0.04)), fill="#111")

        # Minute small ticks
        for minute in range(60):
            if minute % 5 == 0:
                continue
            angle = (minute / 60.0) * 360.0
            x_outer, y_outer = polar_to_cart(self.cx, self.cy, self.radius - 6, angle)
            x_inner, y_inner = polar_to_cart(self.cx, self.cy, self.radius - 12, angle)
            self.canvas.create_line(x_inner, y_inner, x_outer, y_outer, width=1)

    def update_clock(self):
        h_ang, m_ang, s_ang = time_to_angles()

        # Calculate endpoints
        hx, hy = polar_to_cart(self.cx, self.cy, self.radius * HOUR_LEN, h_ang)
        mx, my = polar_to_cart(self.cx, self.cy, self.radius * MIN_LEN, m_ang)
        sx, sy = polar_to_cart(self.cx, self.cy, self.radius * SEC_LEN, s_ang)

        # Update hands (set color after coords)
        self.canvas.coords(self.hour_hand, self.cx, self.cy, hx, hy)
        self.canvas.itemconfigure(self.hour_hand, fill=HOUR_COLOR)

        self.canvas.coords(self.min_hand, self.cx, self.cy, mx, my)
        self.canvas.itemconfigure(self.min_hand, fill=MIN_COLOR)

        self.canvas.coords(self.sec_hand, self.cx, self.cy, sx, sy)
        self.canvas.itemconfigure(self.sec_hand, fill=SEC_COLOR)

        # Schedule next update
        self.after(UPDATE_MS, self.update_clock)


if __name__ == "__main__":
    app = AnalogClock(size=SIZE)
    app.mainloop()