// PlayerController.cs
// Lab 9 - Experiment 9: Simple Interactive 3D Scene using Unity
// Moves a rigid-body sphere with the keyboard and lets it jump.

using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
public class PlayerController : MonoBehaviour
{
    [Header("Movement")]
    public float moveForce = 15f;       // force while a key is held
    public float jumpImpulse = 6f;      // upward impulse of one jump
    public Transform cameraTransform;   // movement is relative to this

    [Header("Respawn")]
    public float fallLimit = -10f;      // below this height we respawn

    private Rigidbody rb;
    private Vector3 startPosition;
    private bool isGrounded;

    void Awake()
    {
        rb = GetComponent<Rigidbody>();
        startPosition = transform.position;
    }

    void FixedUpdate()
    {
        float h = Input.GetAxis("Horizontal"); // A / D or arrow keys
        float v = Input.GetAxis("Vertical");   // W / S or arrow keys

        // Flatten the camera axes so the ball never pushes up or down.
        Vector3 forward = Vector3.forward;
        Vector3 right = Vector3.right;

        if (cameraTransform != null)
        {
            forward = Vector3.ProjectOnPlane(cameraTransform.forward, Vector3.up).normalized;
            right = Vector3.ProjectOnPlane(cameraTransform.right, Vector3.up).normalized;
        }

        Vector3 direction = forward * v + right * h;
        rb.AddForce(direction * moveForce);
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space) && isGrounded)
        {
            rb.AddForce(Vector3.up * jumpImpulse, ForceMode.Impulse);
            isGrounded = false;
        }

        if (transform.position.y < fallLimit)
        {
            Respawn();
        }
    }

    // The ball is grounded while a contact normal points mostly upward.
    void OnCollisionStay(Collision collision)
    {
        foreach (ContactPoint contact in collision.contacts)
        {
            if (contact.normal.y > 0.5f)
            {
                isGrounded = true;
                return;
            }
        }
    }

    void OnCollisionExit(Collision collision)
    {
        isGrounded = false;
    }

    void Respawn()
    {
        // Switching to kinematic and back clears all velocities.
        rb.isKinematic = true;
        transform.position = startPosition;
        rb.isKinematic = false;
    }
}
