using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityStandardAssets.Characters.ThirdPerson;

public class JumpPadScript : MonoBehaviour
{

    private bool disabled = false;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    void OnTriggerEnter(Collider other) {
        if (other.name == "Akaza" && !this.disabled) {
            Debug.Log("ぶつかったぞ！");
            this.GetComponent<Renderer>().material.color = Color.black;
            var ctrl = other.GetComponent<ThirdPersonUserControl>();
            ctrl.m_Jump = true;
            // this.disabled = true;
        }
    }
}
