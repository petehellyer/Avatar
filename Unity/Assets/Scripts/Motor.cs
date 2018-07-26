// This code Links the avatar to the computational model. Adapted from Standard Assets

using System;
using UnityEngine;
using MakeNetworkNamespace;

public class Motor : MonoBehaviour
{
	// Unity Hooks to Computational Model and the Actor.
	public GameObject BaseObject;
	private float previousCount;
	private bool statechange;
	public float v;
	public float h;
	public float pre_v;
	public float pre_h;
	public GameObject ColliderObject;

	private void Start()
    {
		// Initialise some properties for the character
		statechange = false;
		previousCount = -1;
		pre_v=0;
		pre_h=0;
        //m_Character = GetComponent<ThirdPersonCharacter>();

    }
    private void Update()
    {
		// get information about the current timestep
		float TimeCount = BaseObject.GetComponent<ModelLogic>().T;
		// only change the state of the character if time is increasing.
		if (previousCount != TimeCount) {
			statechange = true;
			previousCount = TimeCount;
		}
		else statechange = false;
		if (statechange) {

			int[] StateNow = BaseObject.GetComponent<ModelLogic>().StatesNow; 
			// read indicies for the motor and sensory nodes from the MakeNetwork object.
			int[] RandomIndices = BaseObject.GetComponent<ModelLogic>().RandomIndices; 
				
			v = 0.0f;
			h = 0.0f;

			// Rotate Left if motor node is active.
			if (StateNow [RandomIndices[0]+33]==2 && StateNow [RandomIndices[0]]!=2)
				{h = h + 1;
				}
			// Rotate Right if right motor node is active.
			if (StateNow [RandomIndices[0]+33]!=2 && StateNow [RandomIndices[0]]==2)
				{h = h - 1;
				}

			// As it happens, stick the character somewhere specific if needed.
			if (BaseObject.GetComponent<ModelLogic> ().T==0)
			{transform.position = new Vector3(1000,1000,1000);}

			// If the BOTH forward nodes are active, move character forward.
			if (StateNow [RandomIndices[1]+33]==2 && StateNow [RandomIndices[1]]==2)
			{v = v + 2.0f; //overall amount of force to move forwards!
			}
			// Move character forward just a little bit, if only one node is active
			else if (StateNow [RandomIndices[1]]!=2 && StateNow [RandomIndices[1]+33]==2)
			{v = v + 0.5f;
			}
			else if (StateNow [RandomIndices[1]]==2 && StateNow [RandomIndices[1]+33]!=2)
			{v = v + 0.50f;
			}
			// Prevent V from being silly high.
			if (v > 5.0f) { // this sets the maximum forwards movement, so use with care!
				v = 5.0f;
			}
			// decay both move commands over time.
			h=(7*h+1*pre_h)/8*0.5f;
			v=(7*v+1*pre_v)/8*0.1f;
			pre_h=h;
			pre_v=v;
		}
		if (BaseObject.GetComponent<ModelLogic> ().Move) {

		// actually move the character
		GetComponent<Rigidbody> ().velocity = (transform.forward * v * 100); // set forward velocity.
		GetComponent<Rigidbody> ().angularVelocity = new Vector3(0, 1, 0) * h * 100; //  set angular velocity
		}
		if (transform.position[1] < 500){
				transform.position = new Vector3(1000,1000,1000); // forced respawn if you fall out of the maze.
		}
	}
}
