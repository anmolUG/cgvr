# Computer Graphics Laboratory — Lab 10 (Experiment 10)
## 3D Viewing Pipeline: Projection and Viewport Mapping

Implementation in Python using **PyOpenGL** (with zero reliance on OpenGL's matrix stack or `gluPerspective` — every matrix, clipping, perspective divide, and viewport mapping is implemented explicitly by hand).

---

## 1. Aim of the Experiment
To write and execute a Python program using PyOpenGL that implements the complete 3D viewing pipeline by hand:
1. **Model Transformation**: Object local space $\rightarrow$ World space.
2. **View (Look-At) Transformation**: World space $\rightarrow$ Eye (camera) space.
3. **Projection Transformation**: Eye space $\rightarrow$ Clip space (both Perspective and Orthographic).
4. **Near-Plane Clipping**: Clipping line segments in homogeneous 4D clip space before perspective division.
5. **Perspective Divide**: Clip space $\rightarrow$ Normalized Device Coordinates (NDC) in $[-1, 1]^3$.
6. **Viewport Transformation**: NDC $\rightarrow$ Window pixel coordinates $(x_{\text{win}}, y_{\text{win}}, z_{\text{win}})$.

The program displays a yellow wireframe cube, a cyan pyramid, and RGB coordinate axes in two side-by-side viewports to compare perspective foreshortening against orthographic projection.

---

## 2. Directory Structure in `cgvr10/`

```
cgvr10/
├── viewing_pipeline.py      # Main PyOpenGL program implementing the hand-written pipeline
├── verify_pipeline.py       # Standalone mathematical test suite (all 10 verification checks)
├── pipeline_tkinter.py      # Appendix 10: Tkinter fallback using only Python standard library
├── interactive_pipeline.html# Browser-based interactive visualizer with live matrix trace
└── README.md                # Full lab manual, mathematical derivations & viva answers
```

---

## 3. Theory & Mathematical Derivations

### 3.1 The 6-Stage Viewing Pipeline

$$\mathbf{P}_{\text{local}} \xrightarrow{\mathbf{M}} \mathbf{P}_{\text{world}} \xrightarrow{\mathbf{V}} \mathbf{P}_{\text{eye}} \xrightarrow{\mathbf{P}} \mathbf{P}_{\text{clip}} \xrightarrow{\text{Clip}} \mathbf{P}'_{\text{clip}} \xrightarrow{\div w} \mathbf{P}_{\text{ndc}} \xrightarrow{\text{Viewport}} \mathbf{P}_{\text{window}}$$

| Stage | Space After Stage | Operation | Mathematical Formula / Matrix |
|:---:|---|---|---|
| **1. Model** | World space | Positions, rotates & scales objects | $\mathbf{M} = \mathbf{T}(\text{offset}) \cdot \mathbf{R}_y(\text{yaw}) \cdot \mathbf{R}_x(\text{pitch})$ |
| **2. View** | Eye (Camera) space | Positions camera at origin looking down $-Z$ | $\mathbf{V} = \text{look\_at}(\mathbf{E}, \mathbf{T}, \mathbf{U})$ |
| **3. Projection** | Clip space | Encodes perspective frustum or orthographic box | $\mathbf{P}_{\text{persp}}$ or $\mathbf{P}_{\text{ortho}}$ |
| **4. Clipping** | Clip space | Clips geometry against view volume ($z = -w$) | Discards if $d < 0$; interpolates intersection point |
| **5. Perspective Divide** | NDC $[-1, 1]^3$ | Non-linear division by $w = -z_{\text{eye}}$ | $(x/w, y/w, z/w)$ |
| **6. Viewport Mapping** | Window pixels | Maps $[-1, 1]^2$ to viewport rectangle $(v_x, v_y, v_w, v_h)$ | $x_w = v_x + \frac{x+1}{2}v_w$, $y_w = v_y + \frac{y+1}{2}v_h$ |

---

### 3.2 Matrix Formulations (Column-Vector Convention)

#### 1. Look-At View Matrix $\mathbf{V}$
Constructs an orthonormal camera basis from camera eye $\mathbf{E}$, target $\mathbf{T}$, and up vector $\mathbf{U}$:
$$\mathbf{f} = \frac{\mathbf{T} - \mathbf{E}}{\|\mathbf{T} - \mathbf{E}\|}, \quad \mathbf{s} = \frac{\mathbf{f} \times \mathbf{U}}{\|\mathbf{f} \times \mathbf{U}\|}, \quad \mathbf{u} = \mathbf{s} \times \mathbf{f}$$

$$\mathbf{V} = \begin{bmatrix} s_x & s_y & s_z & -\mathbf{s} \cdot \mathbf{E} \\ u_x & u_y & u_z & -\mathbf{u} \cdot \mathbf{E} \\ -f_x & -f_y & -f_z & \mathbf{f} \cdot \mathbf{E} \\ 0 & 0 & 0 & 1 \end{bmatrix}$$
*Note: The third row uses $-\mathbf{f}$ because the camera views along the negative $Z$ axis.*

#### 2. Perspective Projection Matrix $\mathbf{P}_{\text{persp}}$
With $c = \cot(\theta/2) = \frac{1}{\tan(\theta/2)}$ and aspect ratio $a = \frac{w}{h}$:
$$\mathbf{P}_{\text{persp}} = \begin{bmatrix} \frac{c}{a} & 0 & 0 & 0 \\ 0 & c & 0 & 0 \\ 0 & 0 & \frac{f+n}{n-f} & \frac{2fn}{n-f} \\ 0 & 0 & -1 & 0 \end{bmatrix}$$
- Row 4 is $[0, 0, -1, 0]$, copying $-z_{\text{eye}}$ into $w_{\text{clip}}$.
- Near plane $z_{\text{eye}} = -n \implies z_{\text{ndc}} = -1$.
- Far plane $z_{\text{eye}} = -f \implies z_{\text{ndc}} = +1$.

#### 3. Orthographic Projection Matrix $\mathbf{P}_{\text{ortho}}$
$$\mathbf{P}_{\text{ortho}} = \begin{bmatrix} \frac{2}{r-l} & 0 & 0 & -\frac{r+l}{r-l} \\ 0 & \frac{2}{t-b} & 0 & -\frac{t+b}{t-b} \\ 0 & 0 & -\frac{2}{f-n} & -\frac{f+n}{f-n} \\ 0 & 0 & 0 & 1 \end{bmatrix}$$
- Row 4 is $[0, 0, 0, 1]$, leaving $w_{\text{clip}} = 1$. The perspective divide produces no scaling.

---

### 3.3 Homogeneous Near-Plane Clipping
Clipping **must occur in clip space before the perspective divide**. Points behind the camera have $w < 0$; dividing by negative $w$ inverts coordinates, projecting objects behind the camera upside-down onto the screen.

For an edge from $\mathbf{C}_0$ to $\mathbf{C}_1$, the signed distance to the near plane $z = -w$ is:
$$d_i = z_{\text{clip}, i} + w_{\text{clip}, i}$$
- $d_0 \ge 0$ and $d_1 \ge 0$: Edge is entirely inside; keep.
- $d_0 < 0$ and $d_1 < 0$: Edge is entirely behind near plane; discard.
- One end inside, one outside: Calculate intersection parameter $t$:
  $$t = \frac{d_0}{d_0 - d_1}, \quad \mathbf{C}_{\text{hit}} = \mathbf{C}_0 + t(\mathbf{C}_1 - \mathbf{C}_0)$$

---

### 3.4 Worked Example (Hand Trace of Cube Vertex $(1, 1, 1)$)

For $\mathbf{E} = (0, 0, 5)$, $\mathbf{T} = (0, 0, 0)$, $\theta = 90^\circ$ ($c = 1.0$), $a = 1.0$, $n = 1.0$, $f = 100.0$, Viewport $800 \times 800$ at $(0, 0)$:

1. **World**: $\mathbf{P}_{\text{world}} = (1, 1, 1, 1)$
2. **Eye**: $\mathbf{V} \cdot \mathbf{P}_{\text{world}} = (1, 1, 1 - 5, 1) = (1, 1, -4, 1)$
3. **Clip**:
   - $x_{\text{clip}} = 1 \times 1 = 1.0$
   - $y_{\text{clip}} = 1 \times 1 = 1.0$
   - $z_{\text{clip}} = \frac{101}{-99}(-4) + \frac{200}{-99} = 4.0808 - 2.0202 = 2.0606$
   - $w_{\text{clip}} = -z_{\text{eye}} = 4.0$
   - $\mathbf{P}_{\text{clip}} = (1.0, 1.0, 2.0606, 4.0)$
4. **NDC**: $\mathbf{P}_{\text{ndc}} = \left(\frac{1}{4}, \frac{1}{4}, \frac{2.0606}{4}\right) = (0.25, 0.25, 0.5152)$
5. **Window**:
   - $x_{\text{win}} = 0 + \frac{0.25 + 1}{2} \times 800 = \mathbf{500.0}$
   - $y_{\text{win}} = 0 + \frac{0.25 + 1}{2} \times 800 = \mathbf{500.0}$
   - $z_{\text{win}} = \frac{0.5152 + 1}{2} = \mathbf{0.7576}$

---

## 4. Execution Guide

### Method 1: PyOpenGL Implementation
Run from `cgvr10/`:
```bash
python viewing_pipeline.py
```

#### Controls
| Key | Action |
|:---:|---|
| **Arrow Keys** | Rotate objects (Left/Right: Yaw, Up/Down: Pitch) |
| **+ / -** | Move camera distance closer / further |
| **[ / ]** | Decrease / increase Field of View (FOV) |
| **n / m** | Move Near Plane closer / further |
| **Space** | Toggle automatic rotation |
| **p** | Print exact pipeline stage coordinates for vertex $(1, 1, 1)$ to terminal |
| **r** | Reset camera and rotations to default |
| **q / Esc** | Quit application |

---

### Method 2: Numerical Verification Script (No GUI Needed)
Run the headless test suite to verify all mathematical invariants:
```bash
python verify_pipeline.py
```

Expected Output:
```
PASS 1. View matrix sends the eye to the origin
    eye -> (0.0, 0.0, 0.0, 1.0)
PASS 2. Target lies on -z at distance 5
    target -> (0.0, 0.0, -5.0, 1.0)
PASS 3. Near plane -> NDC z = -1, far plane -> +1
    near -1.0000 far 1.0000
PASS 4. Clip w = -z(eye) = 4 for the point (1, 1, 1)
    clip = (1.0, 1.0, 2.0606, 4.0)
PASS 5. Vertex (1,1,1): NDC = (0.25, 0.25, 0.5152)
    ndc = (0.25, 0.25, 0.5152)
PASS    Window position = (500, 500) in an 800 x 800 viewport
    window = (500.0, 500.0, 0.7576)
PASS 6. Origin maps to the viewport centre (400, 400)
PASS 7. NDC corners map to the viewport corners
    lower-left (100.0, 50.0, 0.0) upper-right (740.0, 530.0, 1.0)
PASS 8. Perspective: width 2 at depth 4 is twice that at depth 8
    0.5000 and 0.2500
PASS    Orthographic: width is the same at every depth
    0.4000 and 0.4000
PASS 9. Edge crossing the near plane is cut at z = -w
    cut point clip = (0.0, 0.0, -1.0, 1.0)
PASS    Edge wholly behind the camera is discarded
PASS 10. fov 90: the point (3, 0, -3) lies on the NDC edge x = 1
    ndc x = 1.0000

ALL TESTS PASSED
```

---

### Method 3: Standard Library Tkinter Version
If PyOpenGL/GLUT is unavailable:
```bash
python pipeline_tkinter.py
```
Provides GUI sliders for Yaw, Pitch, Camera Distance, and FOV.

---

### Method 4: Browser-Based Interactive Visualizer
Open `interactive_pipeline.html` in any web browser to interactively drag sliders and observe the real-time matrix breakdown.

---

## 5. Review & Viva Voce Questions with In-Depth Answers

### Q1: List the stages of the 3D viewing pipeline in order.
**Answer:**
1. **Model Transformation** (Local $\rightarrow$ World)
2. **View Transformation** (World $\rightarrow$ Eye/Camera)
3. **Projection Transformation** (Eye $\rightarrow$ Clip)
4. **Primitive Clipping** (in Clip space against view volume planes)
5. **Perspective Division** (Clip $\rightarrow$ Normalized Device Coordinates $[-1, 1]^3$)
6. **Viewport Transformation** (NDC $\rightarrow$ Window pixel coordinates)

### Q2: What is the difference between local, world, and eye coordinates?
**Answer:**
- **Local coordinates**: Relative to the object's own origin/center.
- **World coordinates**: Relative to the global scene origin, positioning multiple objects together.
- **Eye (camera) coordinates**: Relative to the camera position as origin, where the camera looks down the negative $Z$ axis with $+Y$ up and $+X$ right.

### Q3: What does the model matrix do, and what does the view matrix do?
**Answer:**
- The **Model matrix** ($\mathbf{M}$) transforms vertices from an object's local frame into the global world frame via translation, rotation, and scaling.
- The **View matrix** ($\mathbf{V}$) transforms the entire world such that the virtual camera sits at the origin $(0, 0, 0)$ aligned with the coordinate axes, looking down $-Z$.

### Q4: Explain how the look-at matrix is built from an eye, a target, and an up vector.
**Answer:**
1. Calculate the forward direction: $\mathbf{f} = \frac{\mathbf{T} - \mathbf{E}}{\|\mathbf{T} - \mathbf{E}\|}$.
2. Calculate the perpendicular right/side vector: $\mathbf{s} = \frac{\mathbf{f} \times \mathbf{U}}{\|\mathbf{f} \times \mathbf{U}\|}$.
3. Calculate the true orthogonal up vector: $\mathbf{u} = \mathbf{s} \times \mathbf{f}$.
4. Construct a $4 \times 4$ matrix whose rows are $\mathbf{s}$, $\mathbf{u}$, and $-\mathbf{f}$, combined with a translation by $-\mathbf{E}$ through dot products: $-\mathbf{s}\cdot\mathbf{E}, -\mathbf{u}\cdot\mathbf{E}, \mathbf{f}\cdot\mathbf{E}$.

### Q5: Why does the third row of the view matrix use $-f$?
**Answer:** In the standard right-handed eye space convention (adopted by OpenGL), the camera looks down the **negative $Z$ axis**. Since $\mathbf{f}$ points forward from the eye to the target, the eye-space $Z$ axis must point in the opposite direction ($-\mathbf{f}$).

### Q6: What is the view volume? Name its shape for perspective and for orthographic projection.
**Answer:** The view volume is the finite 3D region of space visible to the camera, bounded by six clipping planes (left, right, bottom, top, near, far).
- **Perspective**: A truncated pyramid called a **frustum**.
- **Orthographic**: A rectangular cuboid or **box**.

### Q7: Derive $x_p = d \cdot \frac{x}{-z}$ using similar triangles.
**Answer:**
Consider the $XZ$ plane where the eye is at $(0,0,0)$ looking along $-Z$. A 3D point has coordinates $(x, z)$ with $z < 0$ (so distance is $-z$). A projection screen is placed at distance $d$ in front of the eye ($z = -d$). By similar right-angled triangles:
$$\frac{x_p}{d} = \frac{x}{-z} \implies x_p = d \cdot \frac{x}{-z}$$

### Q8: Why is the fourth row of the perspective matrix $(0, 0, -1, 0)$?
**Answer:** A linear matrix multiplication cannot perform division by a variable coordinate $z$. By setting the 4th row to $(0, 0, -1, 0)$, the product yields:
$$w_{\text{clip}} = 0\cdot x + 0\cdot y + (-1)\cdot z + 0\cdot 1 = -z$$
This stores the distance $-z$ into the homogeneous coordinate $w$, enabling the division $(x/w, y/w)$ to be performed in the perspective divide stage.

### Q9: What is the meaning of $w$ in homogeneous coordinates? Why is it not 1 after projection?
**Answer:** In affine space, $w=1$ represents a position vector, while $w=0$ represents a direction vector. After perspective projection, $w$ holds the camera distance $-z_{\text{eye}}$ to enable non-linear perspective foreshortening during the perspective divide.

### Q10: What is the field of view and how does it enter the perspective matrix?
**Answer:** Field of view ($\theta$ or FOV) is the vertical angular extent of the visible scene. It determines the scaling factor:
$$c = \cot\left(\frac{\theta}{2}\right) = \frac{1}{\tan(\theta/2)}$$
which occupies diagonal entries $P_{11} = c/a$ and $P_{22} = c$.

### Q11: Why is the aspect ratio needed in the projection matrix?
**Answer:** Most viewports are wider than they are tall ($a = w/h > 1$). Without dividing $x$ by $a$, geometry would be horizontally stretched to fill the non-square window. Dividing $c$ by $a$ preserves true geometric proportions.

### Q12: Write the orthographic projection matrix. Why does $w$ remain 1?
**Answer:**
$$\mathbf{P}_{\text{ortho}} = \begin{bmatrix} \frac{2}{r-l} & 0 & 0 & -\frac{r+l}{r-l} \\ 0 & \frac{2}{t-b} & 0 & -\frac{t+b}{t-b} \\ 0 & 0 & -\frac{2}{f-n} & -\frac{f+n}{f-n} \\ 0 & 0 & 0 & 1 \end{bmatrix}$$
The fourth row is $[0, 0, 0, 1]$, so $w_{\text{clip}} = 1\cdot w = 1$. Because $w=1$, no depth division occurs, preserving parallel lines and scale independent of depth.

### Q13: Compare perspective and orthographic projection with two examples of use.
**Answer:**
- **Perspective**: Parallel lines converge toward vanishing points; objects farther away appear smaller. *Use cases*: First-person video games, architectural renderings, flight simulators.
- **Orthographic**: Parallel lines remain parallel; scale is independent of distance. *Use cases*: CAD mechanical blueprints, 2D tile games, architectural floor plans.

### Q14: What is clip space? What is the condition for a point to be inside the view volume?
**Answer:** Clip space is the 4D homogeneous coordinate space immediately following multiplication by the projection matrix. A point is inside the view volume if and only if:
$$-w \le x \le w, \quad -w \le y \le w, \quad -w \le z \le w$$

### Q15: Why must clipping be done before the perspective divide?
**Answer:** For points behind the camera, $w = -z_{\text{eye}} < 0$. Dividing by a negative $w$ reverses signs, causing geometry behind the camera to reflect erroneously into the view volume as an inverted "phantom" image. Performing clipping when $w$ and $z$ are in clip space prevents division by zero or negative $w$.

### Q16: Explain the formula $t = \frac{d_0}{d_0 - d_1}$ used to clip an edge.
**Answer:** The signed distance of an end point to the plane $z = -w$ is $d = z + w$. For a line parameterized by $\mathbf{C}(t) = \mathbf{C}_0 + t(\mathbf{C}_1 - \mathbf{C}_0)$, the plane is crossed when $d(t) = d_0 + t(d_1 - d_0) = 0$. Solving for $t$ gives $t = \frac{d_0}{d_0 - d_1}$.

### Q17: What is the perspective divide? What are normalised device coordinates?
**Answer:**
- **Perspective divide**: Dividing the clip space coordinates by $w$: $(x/w, y/w, z/w)$.
- **Normalised Device Coordinates (NDC)**: A canonical cube spanning $[-1, 1]^3$, independent of screen resolution and aspect ratio.

### Q18: Write the viewport transformation formulas.
**Answer:** For a viewport rectangle starting at $(v_x, v_y)$ with width $v_w$ and height $v_h$:
$$x_{\text{win}} = v_x + \frac{x_{\text{ndc}} + 1}{2} \cdot v_w$$
$$y_{\text{win}} = v_y + \frac{y_{\text{ndc}} + 1}{2} \cdot v_h$$
$$z_{\text{win}} = \frac{z_{\text{ndc}} + 1}{2} \quad (\text{depth in } [0, 1])$$

### Q19: Where does the point at the centre of the NDC cube end up in a viewport of $800 \times 600$ at $(100, 50)$?
**Answer:** The center of NDC is $(0, 0, 0)$:
- $x_{\text{win}} = 100 + \frac{0 + 1}{2} \times 800 = 100 + 400 = \mathbf{500}$
- $y_{\text{win}} = 50 + \frac{0 + 1}{2} \times 600 = 50 + 300 = \mathbf{350}$
- $z_{\text{win}} = \frac{0 + 1}{2} = \mathbf{0.5}$

### Q20: Why does OpenGL window $y$ differ from Tkinter canvas $y$?
**Answer:**
- OpenGL adheres to Cartesian coordinates with the origin $(0, 0)$ at the **bottom-left** of the window ($+Y$ points up).
- Tkinter, HTML5 Canvas, and standard windowing systems place $(0, 0)$ at the **top-left** ($+Y$ points down). Therefore, Tkinter requires $y$ inversion: $y_{\text{win}} = \left(1 - \frac{y_{\text{ndc}}+1}{2}\right) \cdot H$.

### Q21: Why is depth stored non-linearly? What is the consequence for the choice of the near plane?
**Answer:**
Because $z_{\text{ndc}}$ is divided by $-z_{\text{eye}}$, $z_{\text{ndc}} = \frac{A \cdot z_{\text{eye}} + B}{-z_{\text{eye}}}$, which is hyperbolic in depth. Over $50\%$ of the depth precision is consumed within the first few units near the near plane. Consequently, setting the near plane too close to zero creates extreme $Z$-fighting for distant geometry. The near plane should always be placed as far from the eye as possible.

### Q22: What happens if the near plane is set to 0?
**Answer:** If $n = 0$, $P_{34} = \frac{2fn}{n - f} = 0$, and the depth mapping degenerates, resulting in division by zero when calculating the inverse depth or near clipping. The camera cannot project points at distance 0.

### Q23: What does the scissor test do in this program?
**Answer:** `glEnable(GL_SCISSOR_TEST)` restricts all drawing and clearing operations strictly within a specified sub-rectangle (`glScissor(vx, vy, vw, vh)`). This prevents geometry in the left perspective viewport from spilling over into the right orthographic viewport.

### Q24: How does the field of view affect the apparent size of objects?
**Answer:** Increasing FOV decreases $c = \cot(\theta/2)$, compressing more 3D space into the $[-1, 1]$ range, which makes objects appear smaller and introduces wide-angle distortion. Decreasing FOV functions like a telephoto zoom lens, magnifying objects.

### Q25: Which OpenGL functions correspond to the stages of the pipeline implemented in this experiment?
**Answer:**
- **Model**: `glTranslate`, `glRotate`, `glScale`
- **View**: `gluLookAt`
- **Perspective**: `gluPerspective`, `glFrustum`
- **Orthographic**: `glOrtho`
- **Viewport**: `glViewport`
- **Clipping & Divide**: Executed automatically by fixed-function/programmable GPU hardware.

### Q26: Why are the three matrices usually multiplied into a single matrix before being applied to the vertices?
**Answer:**
Matrix multiplication is associative:
$$\mathbf{P}_{\text{clip}} = (\mathbf{P} \cdot \mathbf{V} \cdot \mathbf{M}) \cdot \mathbf{P}_{\text{local}} = \mathbf{MVP} \cdot \mathbf{P}_{\text{local}}$$
Computing the single composite $4 \times 4$ matrix $\mathbf{MVP}$ once per frame/object requires only one matrix-vector multiplication (16 multiplications + 12 additions) per vertex, instead of three separate matrix-vector transforms for thousands or millions of vertices.
