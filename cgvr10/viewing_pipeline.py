# viewing_pipeline.py
# Lab 10 - Experiment 10
# The 3D Viewing Pipeline: Projection and Viewport Mapping
#
# Every stage of the pipeline is written out by hand in Python:
#
# model -> world -> view -> clip -> NDC -> window (viewport) coordinates
#
# OpenGL is used ONLY to draw finished 2D lines in window coordinates.
# The fixed-function matrix stack and gluPerspective are NOT used.
#
# Keys: arrows rotate the objects
#       + / -  move the camera closer / further
#       [ / ]  decrease / increase the field of view
#       n / m  move the near plane closer / further
#       space  start or stop auto-rotation
#       p      print every pipeline stage for one cube vertex
#       r      reset    q or ESC  quit

import sys
import math
from OpenGL.GL import *
from OpenGL.GLUT import *

# ---------------------------------------------------------------
# 1. Vector and 4x4 matrix helpers (column-vector convention)
# ---------------------------------------------------------------
def sub3(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def dot3(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def cross3(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])

def norm3(a):
    n = math.sqrt(dot3(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)

def identity():
    return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)]
            for i in range(4)]

def mat_vec(m, v):
    return tuple(sum(m[i][k] * v[k] for k in range(4)) for i in range(4))

def translate(tx, ty, tz):
    m = identity()
    m[0][3], m[1][3], m[2][3] = tx, ty, tz
    return m

def rotate_x(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]]

def rotate_y(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]]

# ---------------------------------------------------------------
# 2. The pipeline matrices
# ---------------------------------------------------------------
def look_at(eye, target, up):
    """View matrix: moves the world so the camera sits at the origin
    looking down the negative z axis."""
    f = norm3(sub3(target, eye))  # forward
    s = norm3(cross3(f, up))      # right
    u = cross3(s, f)              # true up
    return [[s[0], s[1], s[2], -dot3(s, eye)],
            [u[0], u[1], u[2], -dot3(u, eye)],
            [-f[0], -f[1], -f[2], dot3(f, eye)],
            [0, 0, 0, 1]]

def perspective(fov_deg, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov_deg) / 2.0)
    return [[f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far),
             2 * far * near / (near - far)],
            [0, 0, -1, 0]]

def orthographic(l, r, b, t, near, far):
    return [[2 / (r - l), 0, 0, -(r + l) / (r - l)],
            [0, 2 / (t - b), 0, -(t + b) / (t - b)],
            [0, 0, -2 / (far - near), -(far + near) / (far - near)],
            [0, 0, 0, 1]]

# ---------------------------------------------------------------
# 3. Clipping, perspective divide and viewport mapping
# ---------------------------------------------------------------
def clip_line_near(c0, c1):
    """Clip a line in CLIP space against the near plane z = -w.
    Returns the two (possibly shortened) end points, or None."""
    d0 = c0[2] + c0[3]  # >= 0 means inside
    d1 = c1[2] + c1[3]
    if d0 < 0 and d1 < 0:
        return None  # wholly behind the near plane
    if d0 >= 0 and d1 >= 0:
        return c0, c1  # wholly inside
    t = d0 / (d0 - d1)  # where the line meets the plane
    hit = tuple(c0[i] + t * (c1[i] - c0[i]) for i in range(4))
    return (hit, c1) if d0 < 0 else (c0, hit)

def perspective_divide(c):
    return (c[0] / c[3], c[1] / c[3], c[2] / c[3])  # NDC in [-1, 1]

def viewport_map(ndc, vx, vy, vw, vh):
    """NDC (-1..1) -> window pixels inside the viewport rectangle."""
    xw = vx + (ndc[0] + 1.0) * 0.5 * vw
    yw = vy + (ndc[1] + 1.0) * 0.5 * vh
    zw = (ndc[2] + 1.0) * 0.5  # depth 0..1
    return (xw, yw, zw)

def trace_vertex(v, model, view, proj, vp):
    """Return every intermediate result for one vertex (for printing)."""
    world = mat_vec(model, (v[0], v[1], v[2], 1.0))
    eye_c = mat_vec(view, world)
    clip = mat_vec(proj, eye_c)
    ndc = perspective_divide(clip)
    win = viewport_map(ndc, *vp)
    return {"world": world, "eye": eye_c, "clip": clip, "ndc": ndc,
            "window": win}

# ---------------------------------------------------------------
# 4. Scene: a cube, a pyramid and coordinate axes
# ---------------------------------------------------------------
CUBE_V = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
          (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
CUBE_E = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
          (0, 4), (1, 5), (2, 6), (3, 7)]
PYR_V = [(-0.8, 0, -0.8), (0.8, 0, -0.8), (0.8, 0, 0.8), (-0.8, 0, 0.8),
         (0, 1.6, 0)]
PYR_E = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 4), (2, 4), (3, 4)]
AXES = [((0, 0, 0), (2.5, 0, 0), (1, 0.2, 0.2)),
        ((0, 0, 0), (0, 2.5, 0), (0.2, 1, 0.2)),
        ((0, 0, 0), (0, 0, 2.5), (0.3, 0.5, 1))]
cam = {"yaw": 25.0, "pitch": 20.0, "dist": 8.0, "fov": 60.0,
       "near": 1.0, "far": 30.0, "spin": False}
WIN_W, WIN_H = 900, 500

def reset():
    cam.update(yaw=25.0, pitch=20.0, dist=8.0, fov=60.0, near=1.0,
               far=30.0, spin=False)

def viewports():
    half = WIN_W // 2
    return (0, 0, half, WIN_H), (half, 0, WIN_W - half, WIN_H)

def view_matrix():
    eye = (0.0, 0.0, cam["dist"])
    return look_at(eye, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))

def model_matrix(offset):
    return mat_mul(translate(*offset),
                   mat_mul(rotate_y(cam["yaw"]), rotate_x(cam["pitch"])))

# ---------------------------------------------------------------
# 5. Drawing an object through the whole pipeline
# ---------------------------------------------------------------
def draw_edges(verts, edges, model, view, proj, vp, colour):
    clip_v = [mat_vec(proj, mat_vec(view, mat_vec(model, (x, y, z, 1.0))))
              for (x, y, z) in verts]
    glColor3f(*colour)
    glBegin(GL_LINES)
    for a, b in edges:
        seg = clip_line_near(clip_v[a], clip_v[b])
        if seg is None:
            continue
        for c in seg:
            xw, yw, _ = viewport_map(perspective_divide(c), *vp)
            glVertex2f(xw, yw)
    glEnd()

def draw_axes(view, proj, vp):
    glBegin(GL_LINES)
    for p0, p1, col in AXES:
        pts = [mat_vec(proj, mat_vec(view, (p[0], p[1], p[2], 1.0)))
               for p in (p0, p1)]
        seg = clip_line_near(pts[0], pts[1])
        if seg is None:
            continue
        glColor3f(*col)
        for c in seg:
            xw, yw, _ = viewport_map(perspective_divide(c), *vp)
            glVertex2f(xw, yw)
    glEnd()

def draw_text(x, y, text):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))

def draw_panel(vp, proj, title):
    vx, vy, vw, vh = vp
    glEnable(GL_SCISSOR_TEST)  # 2D clip to the viewport
    glScissor(vx, vy, vw, vh)
    glClearColor(0.10, 0.11, 0.14, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    view = view_matrix()
    draw_axes(view, proj, vp)
    draw_edges(CUBE_V, CUBE_E, model_matrix((-1.6, 0, 0)), view, proj, vp,
               (0.95, 0.85, 0.30))
    draw_edges(PYR_V, PYR_E, model_matrix((2.2, -0.8, 0)), view, proj, vp,
               (0.40, 0.85, 0.95))
    glDisable(GL_SCISSOR_TEST)
    glColor3f(0.6, 0.6, 0.65)  # viewport border
    glBegin(GL_LINE_LOOP)
    glVertex2f(vx + 1, vy + 1)
    glVertex2f(vx + vw - 1, vy + 1)
    glVertex2f(vx + vw - 1, vy + vh - 1)
    glVertex2f(vx + 1, vy + vh - 1)
    glEnd()
    glColor3f(0.9, 0.9, 0.9)
    draw_text(vx + 10, vy + vh - 20, title)

def display():
    glViewport(0, 0, WIN_W, WIN_H)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, WIN_W, 0, WIN_H, -1, 1)  # units = pixels
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    left, right = viewports()
    aspect = left[2] / float(left[3])
    persp = perspective(cam["fov"], aspect, cam["near"], cam["far"])
    half_h = cam["dist"] * math.tan(math.radians(cam["fov"]) / 2.0)
    half_w = half_h * aspect
    ortho = orthographic(-half_w, half_w, -half_h, half_h,
                         cam["near"], cam["far"])
    draw_panel(left, persp, "PERSPECTIVE fov=%.0f near=%.1f dist=%.1f"
               % (cam["fov"], cam["near"], cam["dist"]))
    draw_panel(right, ortho, "ORTHOGRAPHIC (same camera)")
    glutSwapBuffers()

# ---------------------------------------------------------------
# 6. Events
# ---------------------------------------------------------------
def print_stages():
    left = viewports()[0]
    proj = perspective(cam["fov"], left[2] / float(left[3]), cam["near"],
                       cam["far"])
    r = trace_vertex(CUBE_V[6], model_matrix((-1.6, 0, 0)), view_matrix(),
                     proj, left)
    fmt = lambda t: "(" + ", ".join("%8.3f" % v for v in t) + ")"
    print("Cube vertex (1, 1, 1) through the pipeline:")
    for key in ("world", "eye", "clip", "ndc", "window"):
        print("  %-7s %s" % (key, fmt(r[key])))

def keyboard(key, x, y):
    k = key.decode("utf-8").lower()
    if k in ("q", "\x1b"):
        sys.exit(0)
    elif k in ("+", "="):
        cam["dist"] = max(cam["dist"] - 0.5, 2.0)
    elif k in ("-", "_"):
        cam["dist"] = min(cam["dist"] + 0.5, 25.0)
    elif k == "[":
        cam["fov"] = max(cam["fov"] - 5.0, 15.0)
    elif k == "]":
        cam["fov"] = min(cam["fov"] + 5.0, 120.0)
    elif k == "n":
        cam["near"] = max(cam["near"] - 0.5, 0.1)
    elif k == "m":
        cam["near"] = min(cam["near"] + 0.5, cam["dist"] + 2.0)
    elif k == " ":
        cam["spin"] = not cam["spin"]
    elif k == "p":
        print_stages()
    elif k == "r":
        reset()
    glutPostRedisplay()

def special(key, x, y):
    if key == GLUT_KEY_LEFT:
        cam["yaw"] -= 5.0
    elif key == GLUT_KEY_RIGHT:
        cam["yaw"] += 5.0
    elif key == GLUT_KEY_UP:
        cam["pitch"] += 5.0
    elif key == GLUT_KEY_DOWN:
        cam["pitch"] -= 5.0
    glutPostRedisplay()

def idle():
    if cam["spin"]:
        cam["yaw"] += 0.6
        glutPostRedisplay()

def reshape(w, h):
    global WIN_W, WIN_H
    WIN_W, WIN_H = max(w, 2), max(h, 2)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIN_W, WIN_H)
    glutCreateWindow(b"3D Viewing Pipeline")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
