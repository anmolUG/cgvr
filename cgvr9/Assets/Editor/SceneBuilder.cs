// Assets/Editor/SceneBuilder.cs
// Lab 9 - Experiment 9: Simple Interactive 3D Scene using Unity
// Builds the whole "Collect the Cubes" scene with one menu click.
// Menu: Lab9 > Build Scene (run it in an empty SampleScene)

using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public static class SceneBuilder
{
    [MenuItem("Lab9/Build Scene")]
    static void Build()
    {
        // ---- ground ----
        GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Ground";
        ground.transform.localScale = new Vector3(3f, 1f, 3f);

        // ---- player ----
        GameObject player = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        player.name = "Player";
        player.tag = "Player";
        player.transform.position = new Vector3(0f, 0.5f, 0f);
        player.AddComponent<Rigidbody>();
        PlayerController pc = player.AddComponent<PlayerController>();

        // ---- camera ----
        Camera cam = Camera.main;
        if (cam == null)
        {
            GameObject camGo = new GameObject("Main Camera");
            cam = camGo.AddComponent<Camera>();
            camGo.tag = "MainCamera";
        }
        CameraFollow follow = cam.gameObject.GetComponent<CameraFollow>();
        if (follow == null)
        {
            follow = cam.gameObject.AddComponent<CameraFollow>();
        }
        follow.target = player.transform;
        pc.cameraTransform = cam.transform;

        // ---- lamp (point light toggled with L) ----
        GameObject lamp = new GameObject("Lamp");
        lamp.transform.position = new Vector3(0f, 4f, 0f);
        Light lampLight = lamp.AddComponent<Light>();
        lampLight.type = LightType.Point;
        lampLight.range = 20f;
        lampLight.intensity = 2f;
        LightToggle toggle = lamp.AddComponent<LightToggle>();
        toggle.targetLight = lampLight;

        // ---- eight collectibles on a circle ----
        GameObject folder = new GameObject("Collectibles");
        for (int i = 0; i < 8; i++)
        {
            float angle = i * Mathf.PI * 2f / 8f;
            GameObject c = GameObject.CreatePrimitive(PrimitiveType.Cube);
            c.name = "Collectible_" + i;
            c.transform.SetParent(folder.transform);
            c.transform.localScale = Vector3.one * 0.6f;
            c.transform.position = new Vector3(
                Mathf.Cos(angle) * 8f, 0.8f, Mathf.Sin(angle) * 8f);
            c.GetComponent<BoxCollider>().isTrigger = true;
            c.AddComponent<Collectible>();
        }

        // ---- user interface ----
        GameObject canvasGo = new GameObject("Canvas",
            typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
        Canvas canvas = canvasGo.GetComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;

        TextMeshProUGUI score = MakeText(canvasGo.transform, "ScoreText",
            new Vector2(0f, 1f), new Vector2(20f, -20f),
            TextAlignmentOptions.TopLeft, 36f);
        TextMeshProUGUI win = MakeText(canvasGo.transform, "WinText",
            new Vector2(0.5f, 0.5f), Vector2.zero,
            TextAlignmentOptions.Center, 60f);

        // ---- game manager ----
        GameObject gmObject = new GameObject("GameManager");
        GameManager gm = gmObject.AddComponent<GameManager>();
        gm.scoreText = score;
        gm.winText = win;

        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        Debug.Log("[Lab9] 'Collect the Cubes' scene built successfully!");
    }

    static TextMeshProUGUI MakeText(Transform parent, string name,
        Vector2 anchor, Vector2 position, TextAlignmentOptions align,
        float size)
    {
        GameObject go = new GameObject(name, typeof(RectTransform));
        go.transform.SetParent(parent, false);
        RectTransform rt = go.GetComponent<RectTransform>();
        rt.anchorMin = anchor;
        rt.anchorMax = anchor;
        rt.pivot = anchor;
        rt.anchoredPosition = position;
        rt.sizeDelta = new Vector2(700f, 100f);

        TextMeshProUGUI text = go.AddComponent<TextMeshProUGUI>();
        text.fontSize = size;
        text.alignment = align;
        text.color = Color.white;
        return text;
    }
}
