using UnityEngine;
using System.Collections;
using UnityEngine.UI;

public class WorldLogic : MonoBehaviour {

	public Slider XX;
	public Slider YY;
	public AvatarInterop InteropObject;

	// Use this for initialization
	void Start () {
		gameObject.transform.localScale = new Vector3 (XX.value, 1, YY.value); // scale the world
	}
	
	// Update is called once per frame
	void Update () {
		gameObject.transform.localScale = new Vector3 (XX.value, 1, YY.value); //scale the world

		if (InteropObject.NextSimulation > InteropObject.StepSimulation)
		{
		}
	}
}
