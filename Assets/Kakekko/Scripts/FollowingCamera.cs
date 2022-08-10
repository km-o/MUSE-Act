using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FollowingCamera : MonoBehaviour
{
    GameObject player;
    Vector3 offset;
    // Start is called before the first frame update

    Vector3 up;
    void Start()
    {
        this.player = GameObject.FindWithTag("Player");
        Debug.Assert(this.player != null);
        this.offset = transform.position - this.player.transform.position;

        this.up = new Vector3(0f, 3.0f, 0f);
    }

    // Update is called once per frame
    void Update()
    {
        if(this.player != null) {
            transform.position = this.player.transform.position - this.offset + this.up;
        }
    }
}
