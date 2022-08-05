using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;


public class GoalScript : MonoBehaviour
{
    public GameObject mainPanel;
    public GameObject goalPanel;

    public MUSEScript muse;
    public TextMeshProUGUI clearTimeText;
    // Start is called before the first frame update
    void Start()
    {
        mainPanel.SetActive(true);
        goalPanel.SetActive(false);
    }

  void OnTriggerEnter(Collider other)
  {
        mainPanel.SetActive(false);
        goalPanel.SetActive(true);
        clearTimeText.text = "Time: " + muse.count + "s";
        muse.end = true;
  }
}
