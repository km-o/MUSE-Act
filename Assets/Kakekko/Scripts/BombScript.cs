using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BombScript : MonoBehaviour
{

    ParticleSystem ps;
    // Start is called before the first frame update
    void Start()
    {
        this.ps = GetComponentInChildren<ParticleSystem>();
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    void OnTriggerEnter(Collider other) {
        if(other.CompareTag("Player")) {
            Debug.Log("ぶつかったぞ！！！！");
            this.ps.Play();
            var manager = GameObject.Find("GameManager").GetComponent<ManageScript>();
            manager.GameOver();
            Destroy(other.gameObject);
            Invoke(nameof(SelfDestory), 1.0f);
        }
    }

    void SelfDestory() {
        Destroy(this.gameObject);
    }
}
