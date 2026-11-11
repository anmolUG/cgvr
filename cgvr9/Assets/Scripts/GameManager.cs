// GameManager.cs
// Lab 9 - Experiment 9: Simple Interactive 3D Scene using Unity
// Keeps the score, updates the on-screen text and restarts the scene.

using UnityEngine;
using UnityEngine.SceneManagement;
using TMPro;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    public TextMeshProUGUI scoreText;
    public TextMeshProUGUI winText;

    private int score;
    private int total;

    void Awake()
    {
        Instance = this;
    }

    void Start()
    {
        total = FindObjectsByType<Collectible>(FindObjectsSortMode.None).Length;
        if (winText != null)
        {
            winText.gameObject.SetActive(false);
        }
        UpdateScoreText();
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.R))
        {
            SceneManager.LoadScene(SceneManager.GetActiveScene().name);
        }
    }

    public void AddScore(int amount)
    {
        score += amount;
        UpdateScoreText();

        if (score >= total)
        {
            if (winText != null)
            {
                winText.gameObject.SetActive(true);
                winText.text = "You Win! Press R to restart";
            }
        }
    }

    void UpdateScoreText()
    {
        if (scoreText != null)
        {
            scoreText.text = "Score: " + score + " / " + total;
        }
    }
}
