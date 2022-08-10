using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using uOSC;
using TMPro;

public class CalibScript : MonoBehaviour
{
    private uOscClient client;

    const string CalibrationAddress = "/musePy/calibration";
    const string PredictAddress = "/musePy/predict";

    public TextMeshProUGUI valueText;
    public TextMeshProUGUI rightCounterText;
    public TextMeshProUGUI leftCounterText;

    public GameObject cube;

    private float right;
    private float left;

    private int rightCounter;
    private int leftCounter;

    const int th = 50;

    private ManageScript ms;


    // Start is called before the first frame update
    void Start()
    {
        this.client = GetComponent<uOscClient>();

        var server = GetComponent<uOscServer>();
        server.onDataReceived.AddListener(OnDataReceived);

        this.right = 0.0f;
        this.left = 0.0f;
        this.rightCounter = 0;
        this.leftCounter = 0;

        this.ms = GetComponent<ManageScript>();
    }

    void Forward()
    {
        var pos = this.cube.transform.position;
        pos.z += 0.01f;
        this.cube.transform.position = pos;
    }

    // Update is called once per frame
    void Update()
    {
        if(this.ms.state != ManageScript.GameState.Play) return;
        Forward();
        if(0.8 <= this.right) {
            this.rightCounter++;
            this.leftCounter--;
            if(this.leftCounter < 0) this.leftCounter = 0;

            if(th <= this.rightCounter) {
                var pos = this.cube.transform.position;
                if(pos.x < 19.0f) {
                    pos.x += 1.0f;
                    this.cube.transform.position = pos;
                    Debug.Log("MOVE RIGHT!!!!!!!!!!!!");
                }
                this.rightCounter = 0;
                this.leftCounter  = 0;
            }
        }
        else if (0.8 <= this.left)
        {
            this.leftCounter++;
            this.rightCounter--;
            if (this.rightCounter < 0) this.rightCounter = 0;

            if (th <= this.leftCounter)
            {
                var pos = this.cube.transform.position;
                if(-19.0f < pos.x) {
                    pos.x -= 1.0f;
                    this.cube.transform.position = pos;
                    Debug.Log("MOVE LEFT!!!!!!!!!!!!");
                }
                this.rightCounter = 0;
                this.leftCounter = 0;
            }
            }
        this.valueText.text = string.Format("{0}:{1}", this.left.ToString(), this.right.ToString());
        this.rightCounterText.text = this.rightCounter.ToString();
        this.leftCounterText.text = this.leftCounter.ToString();
    }

    public void StartCalibration()
    {
        this.client.Send("/museUnity", "start");
        Debug.Log("sent /museUnity, start");
    }

    public void StopCalibration() 
    {
        this.client.Send("/museUnity", "end");
        Debug.Log("sent /museUnity, end");
    }

    public void OnClick() {
        StartCalibration();
    }

    public void OnDataReceived(Message msg) 
    {
        if(msg.address == CalibrationAddress) {
            var values = msg.values;
            if (values.Length == 0) return;
            // 暗黙の右キャリブレ
            if ((string)values[0] == "start")
            {
                this.ms.state = ManageScript.GameState.Calibration;
                Debug.Log("Calibration Start!");
            }
            if ((string)values[0] == "right")
            {
                Debug.Log("Calibration Right!");
            }
            else if ((string)values[0] == "left")
            {
                Debug.Log("Cailbration Left!");
            }
            else if ((string)values[0] == "end")
            {
                Debug.Log("Calibration end!");
            }
            else if((string)values[0] == "predStart") 
            {
                this.ms.state = ManageScript.GameState.Play;
                Debug.Log("Predict start!");
            }
            else if ((string)values[0] == "predEnd")
            {
                Debug.Log("Predict end!");  
            }
            else if ((string)values[0] == "error")
            {
                Debug.Log("Calibration ERROR!!!!");
            }
        } else if (msg.address == PredictAddress) {
            var values = msg.values;
            if(values.Length == 0) return;
            Debug.Log("0: "+values[0]);
            Debug.Log("1: "+values[1]);
            this.right = (float)values[0];
            this.left = (float)values[1];
        }
    } 
}
