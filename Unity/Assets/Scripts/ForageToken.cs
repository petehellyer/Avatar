using UnityEngine;
using System.Collections;
using UnityEngine.UI;


public class ForageToken : MonoBehaviour {

	public ForageLogic controller;
	public Text scorecard;
	private int oscseed;
	// Use this for initialization
	void Start () {
		oscseed = Random.Range (1, 100);
	}
	
	// Update is called once per frame
	void Update () {
		// This stuff is all for display and can be disabled if desired..
		Vector3 oldposition = gameObject.transform.position;
		oldposition[1] = Mathf.Sin(Time.fixedTime+oscseed)*0.1f + 1001; // make the token bob up and down a bit. for fun.
		gameObject.transform.position = oldposition;
		Color oldcolor = gameObject.GetComponent<Light> ().color;
		oldcolor.r = Mathf.Clamp (oldcolor.r + Random.Range (-0.05f, 0.05f), 0f, 1f);
		oldcolor.g = Mathf.Clamp (oldcolor.g + Random.Range (-0.05f, 0.05f), 0f, 1f);
		oldcolor.b = Mathf.Clamp (oldcolor.b + Random.Range (-0.05f, 0.05f), 0f, 1f);
		gameObject.GetComponent<Light> ().color = oldcolor; // change the color a bit. for fun.
		gameObject.transform.localScale = Vector3.one * (0.5f + (Mathf.Sin(Time.fixedTime+oscseed)*0.1f));

	}
	void OnTriggerEnter(Collider c){
		if (c.CompareTag("Avatar")) { // only disable if the colling object has the tag "Avatar"
			gameObject.SetActive (false); // disable myself!
			//Debug.LogWarning ("Picked up a token!");
			controller.score++;
		}
	}
}
