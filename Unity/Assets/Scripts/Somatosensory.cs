// This script controls the somatosensory system of the avatar

using UnityEngine;
using System.Collections;
using MakeNetworkNamespace;

public class Somatosensory : MonoBehaviour {

	//Unity Hooks to raytraces and capsule contactor
	public GameObject BaseObject;
	public GameObject LeftEye;
	public GameObject RightEye;
	public bool ShowRaytrace = true;
	public bool ShowCollider = false;
	public bool InContact=false;
	public int[] StateSelected;

	void Update () {
		if (BaseObject.GetComponent<ModelLogic>().Somatosensory == true) {
		// Get motor / sensory nodes from the Model
		int[] RandomIndices = BaseObject.GetComponent<ModelLogic> ().RandomIndices; 
		bool TN = BaseObject.GetComponent<ModelLogic> ().TN;

		StateSelected = BaseObject.GetComponent<ModelLogic> ().StatesSelected; 

		// Perform Raycasting for the Left eye
		RaycastHit hit;
		float distanceToObject = 100;
		Vector3 Pos = new Vector3 (LeftEye.transform.position.x, LeftEye.transform.position.y - 0.8f, LeftEye.transform.position.z);
		Vector3 fwd = LeftEye.transform.TransformDirection (Vector3.right + Vector3.up * -0.2f);

		if (Physics.Raycast (Pos, fwd, out hit, 10.0f)) {
			if (ShowRaytrace) {
				Debug.DrawRay (Pos, fwd);
			}
			distanceToObject = hit.distance;
		}
		// Perform Raycasting for the Right eyea
		RaycastHit hitRE;
		float distanceToObjectRE = 100;
		Vector3 PosR = new Vector3 (RightEye.transform.position.x, LeftEye.transform.position.y - 0.8f, LeftEye.transform.position.z);
		Vector3 fwdR = RightEye.transform.TransformDirection (Vector3.right + Vector3.up * 0.2f);
		if (Physics.Raycast (PosR, fwdR, out hitRE, 10.0f)) {
			if (ShowRaytrace) {
				Debug.DrawRay (PosR, fwdR);
			}
			distanceToObjectRE = hitRE.distance;
		}

		// Left Eye Model Feedback
		// Respond by setting the model to active in somatosensory nodes
		if (distanceToObject < 2) { // near nodes
			Debug.Log ("VIS_L");
			StateSelected [RandomIndices [2]] = 1;
			if (TN) { // If there's a task negative node, switch that OFF
				StateSelected [RandomIndices [5]] = 2;
			}
			} else {// must explicitly switch off stateselected, else it remains selected.
				StateSelected [RandomIndices [2]] = 0;
				if (TN) {
					StateSelected [RandomIndices [5]] = 0;
				}
			}

		// Right Eye Model Feedback
		// Respond by setting the model to active in somatosensory nodes
			if (distanceToObjectRE < 2) {
				Debug.Log ("VIS_R");
				StateSelected [RandomIndices [2] + 33] = 1;
				//StateSelected [RandomIndices [3] + 33] = 0;
				if (TN) {
					StateSelected [RandomIndices [5] + 33] = 2;
				}
			} else { // must explicitly switch off stateselected, else it remains selected.
				StateSelected [RandomIndices [2] + 33] = 0;
				if (TN) {
					StateSelected [RandomIndices [5] + 33] = 0;
				}
			}
	// Collider logic.
		}
	}

	void OnTriggerEnter (Collider col) {
		if (BaseObject.GetComponent<ModelLogic> ().Somatosensory == true) {
			// This void runs when the collider is activated - i.e. the avatar collides with a wall!

			// get some information from the model about what happens here.
			int[] RandomIndices = BaseObject.GetComponent<ModelLogic> ().RandomIndices; 
			int[] StateSelected = BaseObject.GetComponent<ModelLogic> ().StatesSelected; 
			Vector3 P = col.ClosestPointOnBounds (transform.position);
			Vector3 relativePoint = transform.InverseTransformPoint (P); 
			InContact = true;
			bool TN = BaseObject.GetComponent<ModelLogic> ().TN;

			// As with the raytraces, set a node to active as a product of being in the collider.
			if (relativePoint.x < -0.100) { 
				Debug.Log ("COL_R");
				StateSelected [RandomIndices [4]] = 1;
				if (TN) {
					StateSelected [RandomIndices [6]] = 2;
				} 
			} else if (relativePoint.x > 0.100) {
				StateSelected [RandomIndices [4] + 33] = 1;
				Debug.Log ("COL_L");
				if (TN) {
					StateSelected [RandomIndices [6] + 33] = 2;
				} 
			} else {
				Debug.Log ("COL_G");
				StateSelected [RandomIndices [6]] = 0;
				StateSelected [RandomIndices [6] + 33] = 0;
			}
		}
			
	}


	void OnTriggerStay (Collider col) {
		if (BaseObject.GetComponent<ModelLogic> ().Somatosensory == true) {
			// what to do if the collider remains active

			// Get values from the controller
			int[] RandomIndices = BaseObject.GetComponent<ModelLogic> ().RandomIndices; 
			int[] StateSelected = BaseObject.GetComponent<ModelLogic> ().StatesSelected; 
			bool TN = BaseObject.GetComponent<ModelLogic> ().TN;

			InContact = true;
			Vector3 P = col.ClosestPointOnBounds (transform.position);
			Vector3 relativePoint = transform.InverseTransformPoint (P); 

			// Same logic as above.
			if (relativePoint.x < -0.100) { 
				Debug.Log ("COL_R");
				StateSelected [RandomIndices [4]] = 1;
				if (TN) {
					StateSelected [RandomIndices [6]] = 2;
				} 
			} else if (relativePoint.x > 0.100) {
				Debug.Log ("COL_L");
				StateSelected [RandomIndices [4] + 33] = 1;
				if (TN) {
					StateSelected [RandomIndices [6] + 33] = 2;
				} 
			} else {
				Debug.Log ("COL_G");
				StateSelected [RandomIndices [4]] = 1;
				StateSelected [RandomIndices [4] + 33] = 1;
				if (TN) {
					StateSelected [RandomIndices [6]] = 2;
					StateSelected [RandomIndices [6] + 33] = 2;
				}
			}
		}
	}
		
	void OnTriggerExit () {

		// Undo everything when you exit the collider.
		// Get stuff from the model

		int[] RandomIndices = BaseObject.GetComponent<ModelLogic> ().RandomIndices; 
		int[] StateSelected = BaseObject.GetComponent<ModelLogic> ().StatesSelected; 
			
		InContact = false;

		//ensure that ALL Collider relivant nodes are set back to Zero.
		StateSelected [RandomIndices [4]] = 0;
		StateSelected [RandomIndices [4] + 33] = 0;

		StateSelected [RandomIndices [6]] = 0;
		StateSelected [RandomIndices [6] + 33] = 0;


//		if (TN) {
//			StateSelected [RandomIndices [6] + 33] = 1;
//			StateSelected [RandomIndices [6]] = 1;
//		} else {
//			StateSelected [RandomIndices [6] + 33] = 0;
//			StateSelected [RandomIndices [6]] = 0;
//		}
	}
}