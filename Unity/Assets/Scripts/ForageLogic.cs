using UnityEngine;
using System.Collections;
using UnityEngine.UI;

public class ForageLogic : MonoBehaviour {
	public Toggle Forage_on;
	public Text scorecard;
	public GameObject Forgagetoken;
	public GameObject ForageSurface; // object to cover in tokens (needs to be flat)
	public float ylevel; // the height in space to stick counters above the surface.
	public int ncounters = 10; // number of counters to generate
	public int score = 0;
	private bool started = false;

	// Use this for initialization
	void Start () {
		// generate counters

	}
	
	// Update is called once per frame
	void Update () {
		if (Forage_on.isOn && (started == false)) { // set up a game of forage!
			Vector2 origin  = new Vector3();
			Vector2 target = new Vector2 ();

			origin [0] = (ForageSurface.transform.position [0] - ForageSurface.transform.lossyScale [0] / 2);
			origin [1] = (ForageSurface.transform.position [2] - ForageSurface.transform.lossyScale [2] / 2);

			target [0] = (ForageSurface.transform.position [0] + ForageSurface.transform.lossyScale [0] / 2);
			target [1] = (ForageSurface.transform.position [2] + ForageSurface.transform.lossyScale [2] / 2);
			float _ylevel = ForageSurface.transform.position [1] + ylevel;

			for (int i = 1; i <= ncounters; i++) {
				Vector3 pos = new Vector3(Random.Range (origin [0], target [0]),_ylevel,Random.Range (origin [1], target [1]));
				//Debug.LogWarning (pos.ToString ());
				GameObject clone = Instantiate (Forgagetoken, pos, Quaternion.identity) as GameObject;
				clone.name = "Token_" + i.ToString ();
				clone.SetActive (true);

			}
			score = 0;
			scorecard.gameObject.SetActive (true);
			started = true;
		}
		if ((Forage_on.isOn == false) && (started == true)) { // clean up a game of forage
			foreach (GameObject go in GameObject.FindGameObjectsWithTag ("Token"))
			{
				Destroy (go);
			}
			score = 0;
			started = false;
			scorecard.gameObject.SetActive(false);
		}
		scorecard.text = "Tokens collected: " + score.ToString ();
	}
}