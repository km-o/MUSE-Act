using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Goal2Script : MonoBehaviour
{
    ManageScript ms;
    // Start is called before the first frame update
    void Start()
    {
        var gm = GameObject.Find("GameManager");
        this.ms = gm.GetComponent<ManageScript>();
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    void OnTriggerEnter(Collider other)
    {
        this.ms.GameOver();
    }
}
