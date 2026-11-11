# verify_pipeline.py
# Checks every stage of the viewing pipeline without opening a window.

import math
import viewing_pipeline as vp

ok = True

def check(name, condition, detail=""):
    global ok
    ok = ok and condition
    print("%s %s" % ("PASS" if condition else "FAIL", name))
    if detail:
        print("    " + detail)

def near(a, b, tol=1e-9):
    return all(abs(x - y) < tol for x, y in zip(a, b))

def rnd(t, k=4):
    return tuple(round(v, k) for v in t)

EYE, TARGET, UP = (0, 0, 5), (0, 0, 0), (0, 1, 0)
VIEW = vp.look_at(EYE, TARGET, UP)
PROJ = vp.perspective(90.0, 1.0, 1.0, 100.0)
VIEWPORT = (0, 0, 800, 800)

# Test 1: the camera position is moved to the origin
e = vp.mat_vec(VIEW, EYE + (1.0,))
check("1. View matrix sends the eye to the origin",
      near(e, (0, 0, 0, 1)), "eye -> %s" % (rnd(e),))

# Test 2: the look-at target lies on the negative z axis
t = vp.mat_vec(VIEW, TARGET + (1.0,))
check("2. Target lies on -z at distance 5",
      near(t, (0, 0, -5, 1)), "target -> %s" % (rnd(t),))

# Test 3: the near and far planes map to NDC z = -1 and +1
zn = vp.perspective_divide(vp.mat_vec(PROJ, (0, 0, -1.0, 1.0)))
zf = vp.perspective_divide(vp.mat_vec(PROJ, (0, 0, -100.0, 1.0)))
check("3. Near plane -> NDC z = -1, far plane -> +1",
      abs(zn[2] + 1) < 1e-9 and abs(zf[2] - 1) < 1e-9,
      "near %.4f far %.4f" % (zn[2], zf[2]))

# Test 4: clip w equals the distance in front of the camera
c = vp.mat_vec(PROJ, vp.mat_vec(VIEW, (1.0, 1.0, 1.0, 1.0)))
check("4. Clip w = -z(eye) = 4 for the point (1, 1, 1)",
      abs(c[3] - 4.0) < 1e-9, "clip = %s" % (rnd(c),))

# Test 5: full trace of the vertex (1, 1, 1), checked by hand
r = vp.trace_vertex((1, 1, 1), vp.identity(), VIEW, PROJ, VIEWPORT)
check("5. Vertex (1,1,1): NDC = (0.25, 0.25, 0.5152)",
      near(r["ndc"], (0.25, 0.25, 2.0606060606 / 4.0), 1e-6),
      "ndc = %s" % (rnd(r["ndc"]),))
check("   Window position = (500, 500) in an 800 x 800 viewport",
      near(r["window"][:2], (500, 500)),
      "window = %s" % (rnd(r["window"]),))

# Test 6: a point on the view axis maps to the centre of the viewport
r0 = vp.trace_vertex((0, 0, 0), vp.identity(), VIEW, PROJ, VIEWPORT)
check("6. Origin maps to the viewport centre (400, 400)",
      near(r0["window"][:2], (400, 400)))

# Test 7: the NDC corners map to the viewport corners
lo = vp.viewport_map((-1, -1, -1), 100, 50, 640, 480)
hi = vp.viewport_map((1, 1, 1), 100, 50, 640, 480)
check("7. NDC corners map to the viewport corners",
      near(lo, (100, 50, 0)) and near(hi, (740, 530, 1)),
      "lower-left %s upper-right %s" % (rnd(lo, 1), rnd(hi, 1)))

# Test 8: perspective shrinks distant objects, orthographic does not
def width_at(depth, proj):
    a = vp.mat_vec(proj, (-1.0, 0.0, -depth, 1.0))
    b = vp.mat_vec(proj, (1.0, 0.0, -depth, 1.0))
    xb = vp.perspective_divide(b)[0]
    xa = vp.perspective_divide(a)[0]
    return abs(xb - xa)

orth = vp.orthographic(-5, 5, -5, 5, 1, 100)
check("8. Perspective: width 2 at depth 4 is twice that at depth 8",
      abs(width_at(4, PROJ) / width_at(8, PROJ) - 2.0) < 1e-9,
      "%.4f and %.4f" % (width_at(4, PROJ), width_at(8, PROJ)))
check("   Orthographic: width is the same at every depth",
      abs(width_at(4, orth) - width_at(8, orth)) < 1e-9,
      "%.4f and %.4f" % (width_at(4, orth), width_at(8, orth)))

# Test 9: near-plane clipping cuts the edge exactly at z = -w
a = vp.mat_vec(PROJ, (0, 0, -3.0, 1.0))  # in front of the camera
b = vp.mat_vec(PROJ, (0, 0, +3.0, 1.0))  # behind the camera
seg = vp.clip_line_near(a, b)
hit = seg[1]
check("9. Edge crossing the near plane is cut at z = -w",
      abs(hit[2] + hit[3]) < 1e-9,
      "cut point clip = %s" % (rnd(hit),))
check("   Edge wholly behind the camera is discarded",
      vp.clip_line_near(vp.mat_vec(PROJ, (0, 0, 2.0, 1.0)),
                         vp.mat_vec(PROJ, (0, 0, 4.0, 1.0))) is None)

# Test 10: with fov 90, a point at depth d and offset d is on the edge
edge = vp.perspective_divide(vp.mat_vec(PROJ, (3.0, 0.0, -3.0, 1.0)))
check("10. fov 90: the point (3, 0, -3) lies on the NDC edge x = 1",
      abs(edge[0] - 1.0) < 1e-9, "ndc x = %.4f" % edge[0])

print("\nALL TESTS PASSED" if ok else "\nSOME TESTS FAILED")
