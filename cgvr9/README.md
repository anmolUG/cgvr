# Computer Graphics Laboratory — Lab 9 (Experiment 9)
## Simple Interactive 3D Scene using Unity: "Collect the Cubes"

---

## 1. Aim of the Experiment
To create a simple interactive 3D scene in Unity, titled **"Collect the Cubes"**, in which:
- A player-controlled sphere moves and jumps on a ground plane under rigid-body physics.
- A third-person camera trails smoothly behind the player.
- 8 rotating and bobbing cubes arranged along a circle are collected upon contact via physics triggers.
- A point light (lamp) can be switched on and off using keyboard input (`L`).
- The player's score and win condition are rendered dynamically using Unity's Canvas and TextMeshPro.
- The scene can be reset with `R` or upon falling off the edge.

---

## 2. Directory Structure

```
cgvr9/
├── Assets/
│   ├── Editor/
│   │   └── SceneBuilder.cs      # Appendix 10: 1-Click scene generator menu (Lab9 > Build Scene)
│   └── Scripts/
│       ├── PlayerController.cs  # Sphere movement, jump impulse, ground check & respawn
│       ├── Collectible.cs       # Cube spin, sinusoidal bobbing & trigger pickup
│       ├── CameraFollow.cs      # Smooth 3rd-person follow camera with Vector3.SmoothDamp
│       ├── GameManager.cs       # Singleton, score tracking, win condition & scene reload
│       └── LightToggle.cs       # Point light toggle via 'L' key
├── ProjectSettings/
│   └── ProjectVersion.txt       # Unity project configuration version
├── interactive_demo.html        # Complete WebGL/Three.js interactive 3D simulation
└── README.md                    # Comprehensive lab manual, code explanations & viva questions
```

---

## 3. Key Concepts & Theory

### 3.1 Game Engine Architecture & The Game Loop
A game engine coordinates graphics rendering, rigid-body physics, audio, input handling, and gameplay scripting. Unity processes a continuous loop at 30–120+ FPS:
1. **Input Poll**: Reads keyboard, mouse, and gamepad states.
2. **FixedUpdate (Physics)**: Executes on a deterministic fixed timestep (default 0.02s / 50 Hz). Physics forces (`AddForce`) belong here.
3. **Update (Logic)**: Executes once per rendered frame with variable duration `Time.deltaTime`. Single-frame key events (`GetKeyDown`) belong here.
4. **LateUpdate (Camera)**: Executes after all `Update` logic, preventing camera jitter when tracking moving objects.
5. **Rendering & UI**: Mesh draw calls, shader illumination, and Canvas overlays.

### 3.2 Coordinate System & Transformations
- Unity uses a **left-handed coordinate system**:
  - $+X$ = Right
  - $+Y$ = Up
  - $+Z$ = Forward
- `Transform` encapsulates local position, rotation (quaternions internally, Euler angles in Inspector), and scale.

### 3.3 Normal Colliders vs. Triggers
| Feature | Normal Collider (`Is Trigger` unchecked) | Trigger Collider (`Is Trigger` checked) |
|---|---|---|
| **Physics Response** | Solid; objects bounce, collide, and exert normal forces | Non-solid; objects pass right through |
| **Callbacks** | `OnCollisionEnter`, `OnCollisionStay`, `OnCollisionExit` | `OnTriggerEnter`, `OnTriggerStay`, `OnTriggerExit` |
| **Usage** | Floor, walls, barriers | Pickups, zones, checkpoints |

### 3.4 Camera-Relative Movement
To ensure pressing `W` always drives the player away from the camera view:
```csharp
Vector3 forward = Vector3.ProjectOnPlane(cameraTransform.forward, Vector3.up).normalized;
Vector3 right = Vector3.ProjectOnPlane(cameraTransform.right, Vector3.up).normalized;
Vector3 direction = forward * v + right * h;
```

---

## 4. C# Scripts Overview

### 4.1 `PlayerController.cs`
- **Location**: `Assets/Scripts/PlayerController.cs`
- **Role**: Drives the sphere using physics forces (`rb.AddForce(direction * moveForce)`).
- **Ground Detection**: Scans contact normals in `OnCollisionStay` (`contact.normal.y > 0.5f`).
- **Jump**: Applies `ForceMode.Impulse` upward ($v = 6\text{ m/s}$, max jump height $h = \frac{v^2}{2g} \approx 1.83\text{ m}$).
- **Respawn**: If $y < -10$, switches `rb.isKinematic = true` to zero velocities and restores `startPosition`.

### 4.2 `Collectible.cs`
- **Location**: `Assets/Scripts/Collectible.cs`
- **Role**:
  - Continuous yaw rotation: `transform.Rotate(0f, spinSpeed * Time.deltaTime, 0f, Space.World)`.
  - Sinusoidal vertical bobbing: `Mathf.Sin(Time.time * bobSpeed) * bobHeight`.
  - Collision trigger: When `other.CompareTag("Player")` matches, invokes `GameManager.Instance.AddScore(1)` and destroys itself.

### 4.3 `CameraFollow.cs`
- **Location**: `Assets/Scripts/CameraFollow.cs`
- **Role**: Trails the player at offset $(0, 6, -8)$ and smoothly interpolates position using `Vector3.SmoothDamp` in `LateUpdate()`.

### 4.4 `GameManager.cs`
- **Location**: `Assets/Scripts/GameManager.cs`
- **Role**: Singleton pattern (`GameManager.Instance`). Counts active collectibles on `Start()`, updates the TextMeshPro UI, displays `"You Win! Press R to restart"` when score equals total, and reloads active scene upon pressing `R`.

### 4.5 `LightToggle.cs`
- **Location**: `Assets/Scripts/LightToggle.cs`
- **Role**: Detects `Input.GetKeyDown(KeyCode.L)` to toggle `targetLight.enabled = !targetLight.enabled`.

### 4.6 `SceneBuilder.cs` (Appendix 10)
- **Location**: `Assets/Editor/SceneBuilder.cs`
- **Role**: Unity Editor menu script (`Lab9 > Build Scene`) that creates the Plane (30×30m), Player Sphere, 8 Collectibles in a radius 8 circle, Lamp, Camera follow setup, Canvas, and TextMeshPro elements automatically.

---

## 5. Execution Guide

### Option A: Running in Unity Editor (Standard Lab Workflow)
1. Open **Unity Hub** and click **Add** (or **Open**), then select the `cgvr9` folder (or create a new 3D Core project named `CollectTheCubes` and copy the `Assets` folder into it).
2. Ensure TextMeshPro essentials are imported: **Window** → **TextMeshPro** → **Import TMP Essential Resources**.
3. In the Unity Editor menu bar, click:
   $$\text{\textbf{Lab9}} \rightarrow \text{\textbf{Build Scene}}$$
4. The entire scene (Ground, Player, 8 Cubes, Camera follow, Lamp, Canvas, and GameManager) will be assembled automatically!
5. Add the open scene to Build Settings: **File** → **Build Settings** → **Add Open Scenes**.
6. Press the **Play** button (or `Ctrl + P`) and click inside the Game window to play.

### Option B: Instant Playable WebGL / Three.js 3D Simulation
If Unity is not yet installed on your machine, open `interactive_demo.html` in any modern web browser (Edge, Chrome, Firefox).
- Full 3D simulation with identical physics, lighting, rotation, bobbing, trigger collection, camera smoothing, jump impulse, and HUD overlay.

---

## 6. Controls Summary

| Key | Action |
|---|---|
| **W / A / S / D** or **Arrow Keys** | Move sphere forward, left, backward, right (relative to camera view) |
| **Space** | Jump (only allowed while sphere is grounded; no double-jumping) |
| **L** | Toggle the Point Light (Lamp) On / Off |
| **R** | Reload scene / Restart game |
| **Esc / Play Button** | Release mouse / Stop play mode |

---

## 7. Results & Verification Checklist

| # | Test Case | Action | Expected Result | Pass/Fail |
|---|---|---|---|:---:|
| 1 | Compilation | Save all scripts, view Console | 0 errors; scripts attach cleanly | ✅ Pass |
| 2 | Start State | Click Play | Score: 0 / 8; Win text hidden; 8 cubes spinning | ✅ Pass |
| 3 | Movement | Press W, A, S, D | Sphere rolls relative to camera view | ✅ Pass |
| 4 | Camera Follow | Roll sphere around | Camera smoothly tracks without jitter | ✅ Pass |
| 5 | Jump Impulse | Press Space on floor | Single clean jump of ~1.83 m height | ✅ Pass |
| 6 | No Double Jump | Press Space twice in air | Second press is ignored while airborne | ✅ Pass |
| 7 | Trigger Pickup | Roll sphere into a cube | Cube vanishes, score increments to 1 / 8 | ✅ Pass |
| 8 | Trigger Physics | Touch cube | Sphere rolls smoothly through without bouncing | ✅ Pass |
| 9 | Win Condition | Collect all 8 cubes | Win text appears: *"You Win! Press R to restart"* | ✅ Pass |
| 10| Respawn | Roll off plane edge ($y < -10$) | Sphere teleports back to $(0, 0.5, 0)$ at rest | ✅ Pass |
| 11| Lamp Toggle | Press `L` twice | Lamp turns off, then on; lighting alters dynamically | ✅ Pass |
| 12| Restart | Press `R` | Scene reloads to initial state (Score: 0 / 8) | ✅ Pass |

---

## 8. Viva Voce / Review Questions with Answers

### Q1: What is a game engine? Name its main parts.
**Answer:** A game engine is a software development framework providing core infrastructure for real-time 2D/3D applications. Its main parts include:
- **Rendering engine** (rasterization, shaders, lighting, camera frustum culling)
- **Physics engine** (rigid bodies, collisions, triggers, gravity)
- **Audio engine** (3D spatial audio, audio listeners, sound effects)
- **Input system** (polling and events from keyboard, mouse, gamepad)
- **Scripting / Logic layer** (C# Mono/IL2CPP virtual machine)
- **Scene graph / Scene hierarchy editor** and asset pipeline.

### Q2: What is a GameObject, and why does an empty GameObject do nothing?
**Answer:** A `GameObject` is the fundamental base container for all entities in a Unity scene. An empty GameObject has only a `Transform` component (representing position, rotation, and scale in 3D space). It does not render or interact with physics until components (like `MeshRenderer`, `Collider`, `Rigidbody`, or scripts) are attached.

### Q3: What is a component? Give three examples of built-in components.
**Answer:** A component is a modular piece of functionality attached to a GameObject. Examples:
1. `Rigidbody`: Implements Newtonian rigid-body physics and gravity.
2. `MeshRenderer`: Submits the geometry mesh to the graphics pipeline to be drawn.
3. `BoxCollider`: Defines a bounding box shape for collision calculations.

### Q4: Explain the Transform component. What is the difference between local and world coordinates?
**Answer:**
- The `Transform` component stores the position, rotation (as quaternion), and scale of a GameObject.
- **Local coordinates** are relative to the object's parent in the Hierarchy.
- **World coordinates** are absolute coordinates relative to the scene's global origin $(0,0,0)$. For an unparented root object, local and world coordinates are identical.

### Q5: Which coordinate system does Unity use? What does +Y represent?
**Answer:** Unity uses a **left-handed coordinate system** where:
- $+X$ points to the right,
- $+Y$ points **upward** (vertical axis),
- $+Z$ points forward.

### Q6: Why is a parent object useful? What happens to its children when it moves?
**Answer:** A parent object groups multiple GameObjects into a hierarchical transform tree. When a parent is translated, rotated, or scaled, all of its child objects undergo the identical composite transformation in world space.

### Q7: What is a prefab?
**Answer:** A prefab (pre-fabricated asset) is a reusable GameObject template saved to the project's asset database. Changing a prefab updates all instances throughout the game scenes simultaneously.

### Q8: What are the different kinds of lights in Unity? Which one is used for the sun?
**Answer:**
- **Directional Light**: Parallel rays from an infinitely distant source; only rotation matters. **Used for the sun**.
- **Point Light**: Emits light radially in all directions from a single 3D point, falling off with distance (used for the lamp).
- **Spot Light**: Emits light in a cone from a specific point.
- **Area Light**: Emits light from a rectangular surface (baked lighting only).

### Q9: How does the Unity camera relate to the viewing pipeline? What do field of view and clipping planes control?
**Answer:** The Camera component evaluates the synthetic camera viewing pipeline:
- **Field of View (FOV)**: Controls the vertical viewing angle of the perspective frustum.
- **Near and Far Clipping Planes**: Define the minimum and maximum distances from the camera along the z-axis within which geometry is rendered. Anything closer than Near or farther than Far is clipped.

### Q10: What does a Rigidbody do? Why must a moving physics object have one?
**Answer:** A `Rigidbody` transfers control of an object to the PhysX physics engine, subjecting it to forces, torque, gravity, and momentum. A moving object needs a Rigidbody so the physics engine can calculate continuous collision detection; moving a static collider directly via `transform.position` causes high computational cost and physics penetration tunneling.

### Q11: What is a Collider? Why should a physics object be moved with forces rather than by setting its position?
**Answer:** A `Collider` defines the physical boundary of an object for intersection testing. Setting `transform.position` directly teleports the object, bypassing collision sweep tests, which can cause the object to clip through floors and walls. Using forces (`AddForce`) allows the physics solver to accurately resolve collisions and friction.

### Q12: What is the difference between a collision and a trigger? Which methods does each one call?
**Answer:**
- **Collision** (`Is Trigger = false`): Physical obstruction where objects rebound or slide. Calls `OnCollisionEnter`, `OnCollisionStay`, and `OnCollisionExit`.
- **Trigger** (`Is Trigger = true`): Non-physical intersection zone where objects pass freely. Calls `OnTriggerEnter`, `OnTriggerStay`, and `OnTriggerExit`.

### Q13: Explain the difference between Awake, Start, Update, FixedUpdate, and LateUpdate.
**Answer:**
- `Awake()`: Called once when the script instance is initialized, before any `Start()`. Used for internal references (`GetComponent`).
- `Start()`: Called once before the first frame update. Used for cross-object lookups.
- `Update()`: Called every rendered frame; variable timestep. Used for non-physics logic and input key checks.
- `FixedUpdate()`: Called on a deterministic fixed physics interval (e.g. 0.02s). Used for `Rigidbody` force calculations.
- `LateUpdate()`: Called once per frame after all `Update()` methods complete. Used for camera tracking.

### Q14: Why is the force applied in FixedUpdate but the jump key read in Update?
**Answer:**
- Physics calculations run in sync with the physics engine at a constant rate in `FixedUpdate()`.
- `Input.GetKeyDown()` returns `true` only for the single frame in which a key transition occurs. Because `FixedUpdate` does not necessarily run every frame (it may run 0 or multiple times), reading `GetKeyDown` inside `FixedUpdate` can miss player key presses.

### Q15: What is Time.deltaTime and why is it used?
**Answer:** `Time.deltaTime` is the time in seconds elapsed between the previous frame and the current frame. Multiplying speeds by `Time.deltaTime` makes movement frame-rate independent (e.g. an object rotating at $90^\circ \times \text{deltaTime}$ rotates at exactly $90^\circ/\text{s}$ at 30, 60, or 144 FPS).

### Q16: What does Input.GetAxis return? How does GetKeyDown differ from GetKey?
**Answer:**
- `Input.GetAxis("Horizontal")` returns a smoothed float between $-1.0$ and $+1.0$.
- `Input.GetKey()` returns `true` continuously every frame the key remains depressed.
- `Input.GetKeyDown()` returns `true` only during the exact single frame the key was initially pressed down.

### Q17: Explain how camera-relative movement vectors are calculated.
**Answer:** The script projects the camera's forward and right vectors onto the horizontal $XZ$ ground plane by stripping the $Y$ component using `Vector3.ProjectOnPlane(v, Vector3.up)` and normalizing:
$$\vec{d} = \hat{f}_{\text{camera}} \cdot v_{\text{input}} + \hat{r}_{\text{camera}} \cdot h_{\text{input}}$$

### Q18: How does the script detect that the sphere is on the ground?
**Answer:** In `OnCollisionStay(Collision collision)`, it inspects each contact point normal. If `contact.normal.y > 0.5f`, the contact surface is horizontal enough to be considered ground (normal pointing upward), setting `isGrounded = true`. In `OnCollisionExit`, `isGrounded` is cleared.

### Q19: Why does CameraFollow use LateUpdate and SmoothDamp?
**Answer:**
- `LateUpdate` ensures the sphere has completely resolved its movement in `FixedUpdate` / `Update` before the camera repositions, avoiding jitter.
- `Vector3.SmoothDamp` acts as a critically damped spring-damper system, smoothly trailing the target without snapping or overshooting.

### Q20: What is a singleton? Why is GameManager one?
**Answer:** A singleton is a design pattern that ensures only one instance of a class exists globally and provides a static point of access (`GameManager.Instance`). `GameManager` is a singleton so that any collectible or external script can immediately call `GameManager.Instance.AddScore(1)` without needing explicit Inspector object links.

### Q21: What does [RequireComponent(typeof(...))] do?
**Answer:** It automatically adds the required component (such as `Rigidbody` or `Collider`) to the GameObject if not already present, and prevents the user from accidentally deleting that component in the Unity Inspector.

---
