# pipeline_tkinter.py
# The 3D viewing pipeline on a Tkinter canvas (standard library only).

import math
import tkinter as tk

W, H = 600, 450

CUBE = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
        (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
EDGES = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
         (0, 4), (1, 5), (2, 6), (3, 7)]

def project(p, yaw, pitch, dist, fov):
    """Model, view, projection, divide and viewport in one function."""
    x, y, z = p
    a, b = math.radians(yaw), math.radians(pitch)
    x, z = (x * math.cos(a) + z * math.sin(a),
            -x * math.sin(a) + z * math.cos(a))  # model: yaw
    y, z = (y * math.cos(b) - z * math.sin(b),
            y * math.sin(b) + z * math.cos(b))  # model: pitch
    ze = z - dist  # view: camera at +dist
    if ze > -0.1:
        return None  # behind the camera
    c = 1.0 / math.tan(math.radians(fov) / 2.0)
    xn = (c / (W / H)) * x / -ze  # clip x / w
    yn = c * y / -ze  # clip y / w
    return ((xn + 1) * 0.5 * W, (1 - (yn + 1) * 0.5) * H)  # viewport (y inverted for Tkinter)

def main():
    root = tk.Tk()
    root.title("3D Viewing Pipeline - Tkinter")
    canvas = tk.Canvas(root, width=W, height=H, bg="#14161c")
    canvas.pack()

    yaw = tk.Scale(root, from_=-180, to=180, orient="horizontal",
                   label="Yaw", length=400)
    pitch = tk.Scale(root, from_=-90, to=90, orient="horizontal",
                     label="Pitch", length=400)
    dist = tk.Scale(root, from_=3, to=20, orient="horizontal",
                    label="Camera distance", length=400)
    fov = tk.Scale(root, from_=20, to=120, orient="horizontal",
                   label="Field of view", length=400)

    yaw.set(30)
    pitch.set(20)
    dist.set(8)
    fov.set(60)

    for s in (yaw, pitch, dist, fov):
        s.pack()

    def redraw(*_):
        canvas.delete("all")
        pts = [project(v, yaw.get(), pitch.get(), dist.get(), fov.get())
               for v in CUBE]
        for a, b in EDGES:
            if pts[a] and pts[b]:
                canvas.create_line(*pts[a], *pts[b],
                                   fill="#f2d94e", width=2)

    for s in (yaw, pitch, dist, fov):
        s.config(command=redraw)

    redraw()
    root.mainloop()

if __name__ == "__main__":
    main()
