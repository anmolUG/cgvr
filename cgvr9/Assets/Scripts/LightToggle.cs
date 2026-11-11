// LightToggle.cs
// Lab 9 - Experiment 9: Simple Interactive 3D Scene using Unity
// Switches a light on and off when the L key is pressed.

using UnityEngine;

public class LightToggle : MonoBehaviour
{
    public Light targetLight;

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.L) && targetLight != null)
        {
            targetLight.enabled = !targetLight.enabled;
        }
    }
}
