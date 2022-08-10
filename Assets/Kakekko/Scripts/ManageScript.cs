using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ManageScript : MonoBehaviour
{
    public enum GameState 
    {
        Title,
        Calibration,
        Play,
        GameOver,
    }

    public GameState state;

    [SerializeField]

    private GameObject gameOverUI;

    [SerializeField]
    private GameObject titleUI;
    [SerializeField]
    private GameObject playUI;

    private CalibScript c;
    // Start is called before the first frame update
    void Start()
    {
        this.state = GameState.Title;
        this.c = GetComponent<CalibScript>();
    }

    // Update is called once per frame
    void Update()
    {
        switch(this.state)
        {
            case GameState.Title:
                this.titleUI.SetActive(true);
                this.playUI.SetActive(false);
                this.gameOverUI.SetActive(false);
                break;
            case GameState.Play:
                this.titleUI.SetActive(false);
                this.playUI.SetActive(true);
                this.gameOverUI.SetActive(false);
                break;
            case GameState.GameOver:
                this.titleUI.SetActive(false);
                this.playUI.SetActive(false);
                this.gameOverUI.SetActive(true);
                break;
            default:
                this.titleUI.SetActive(false);
                this.playUI.SetActive(false);
                this.gameOverUI.SetActive(false);
                break;
        }
    }

    public void GameOver()
    {
        this.state = GameState.GameOver;
        this.c.StopCalibration();
    }
}
