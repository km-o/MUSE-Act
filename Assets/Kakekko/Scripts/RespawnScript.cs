using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RespawnScript : MonoBehaviour
{
    public GameObject respawn;
    // Update is called once per frame
    void OnTriggerEnter(Collider other)
    {
        other.transform.position = respawn.transform.position;
    }
}
