// CameraFollow.cs
// Lab 9 - Experiment 9: Simple Interactive 3D Scene using Unity
// Third-person camera that trails the player smoothly.

using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    public Transform target;                                 // the player
    public Vector3 offset = new Vector3(0f, 6f, -8f);
    public float smoothTime = 0.15f;                         // catch-up time (s)

    private Vector3 velocity = Vector3.zero;

    // LateUpdate runs after the player has moved in this frame.
    void LateUpdate()
    {
        if (target == null) return;

        Vector3 desired = target.position + offset;
        transform.position = Vector3.SmoothDamp(
            transform.position, desired, ref velocity, smoothTime);
        transform.LookAt(target.position + Vector3.up * 0.5f);
    }
}
