// Collectible.cs
// Lab 9 - Experiment 9: Simple Interactive 3D Scene using Unity
// Spins and bobs a pickup; adds one point when the player touches it.

using UnityEngine;

[RequireComponent(typeof(Collider))]
public class Collectible : MonoBehaviour
{
    public float spinSpeed = 90f;   // degrees per second
    public float bobHeight = 0.25f; // metres
    public float bobSpeed = 2f;     // cycles per 2*pi seconds

    private Vector3 basePosition;

    void Start()
    {
        basePosition = transform.position;
    }

    void Update()
    {
        transform.Rotate(0f, spinSpeed * Time.deltaTime, 0f, Space.World);
        float offset = Mathf.Sin(Time.time * bobSpeed) * bobHeight;
        transform.position = basePosition + Vector3.up * offset;
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            GameManager.Instance.AddScore(1);
            Destroy(gameObject);
        }
    }
}
