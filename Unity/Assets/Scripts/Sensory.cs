// This script controls the somatosensory system of the avatar

using UnityEngine;

public class Sensory : MonoBehaviour
{

	//Unity Hooks to raytraces and capsule contactor
	public GameObject LeftEye;
	public GameObject RightEye;
	public AvatarInterop AvatarIO;
	public bool EyeLeft;
	public bool EyeRight;
	public bool ColliderLeft;
	public bool ColliderRight;
	public bool ShowRaytrace = true;
	private double _NoCollisionDistance = .8;

	void Update ()
	{
		// Only Update Unity if the next simulation point was calculated by Python
		if (AvatarIO.NextSimulation > AvatarIO.StepSimulation)
		{
		// Get motor / sensory nodes from the Model

		// Visual Update
		// -------------------------------------------------------------------------------------------------------------
		// Perform Raycasting for the Left eye
		RaycastHit hitLE;
		float distanceToObjectLE = 100;
		Vector3 Pos = new Vector3 (LeftEye.transform.position.x, LeftEye.transform.position.y - 0.8f, LeftEye.transform.position.z);
		Vector3 fwd = LeftEye.transform.TransformDirection (Vector3.right + Vector3.up * -0.2f);

		if (Physics.Raycast (Pos, fwd, out hitLE, 10.0f)) {
			if (ShowRaytrace) {
				Debug.DrawRay (Pos, fwd);
			}
			// Find coordinates where the Raycast enconter an object
			distanceToObjectLE = hitLE.distance;
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
			// Find coordinates where the Raycast enconter an object
			distanceToObjectRE = hitRE.distance;
		}

		// Left Eye Model Feedback
		// Respond by setting the model to active in somatosensory nodes, if the distance between the Avatar and the hit
		// point is less than 2 units
		if (distanceToObjectLE < 2) { // near nodes
			EyeLeft = true;
			AvatarIO.Visual_L (true);
		} else {// must explicitly switch off stateselected, else it remains selected.
			EyeLeft = false;
			AvatarIO.Visual_L (false);
		}

		// Right Eye Model Feedback
		// Respond by setting the model to active in somatosensory nodes
		if (distanceToObjectRE < 2) {
			EyeRight = true;
			AvatarIO.Visual_R (true);
		} else { // must explicitly switch off stateselected, else it remains selected.
			EyeRight = false;
			AvatarIO.Visual_R (false);
		}
		// Collider logic
		//-------------------------------------------------------------------------------------------------------------
		// Switch off nodes when the Avatar when the distance from the Avatar and the wall is above a prespecified threashold
		if ( (ColliderLeft == true) && (distanceToObjectLE > _NoCollisionDistance) ){
			ColliderLeft = false;
			AvatarIO.Somatosensory_L(false);
			Debug.Log("Deactivate Somatosensory LE");
			}

		if ( (ColliderRight == true) && (distanceToObjectRE > _NoCollisionDistance) ){
			ColliderRight = false;
			AvatarIO.Somatosensory_R(false);
			Debug.Log(" Deactivate Somatosensory RE");
			}
			
		if ( ((ColliderLeft == true) && (ColliderRight == true)) && 
		     ((distanceToObjectLE > _NoCollisionDistance) && (distanceToObjectRE > _NoCollisionDistance)) ){
			ColliderLeft = false;
			ColliderRight = false;
			AvatarIO.Somatosensory_L(false);
			AvatarIO.Somatosensory_R(false);
			Debug.Log("Deactivate Both Somatosensory");
			}
		}
	}

	private void OnControllerColliderHit(ControllerColliderHit hit)
	{
		// This void runs when the avatar collides with a wall!
		//var relativePoint = (hit.point - transform.position).normalized;
		// Transforms the hitpoint from world space to local space
		Vector3 relativePoint = transform.InverseTransformPoint(hit.point);
		Vector3 Position = transform.position;

		// As with the raytraces, set a node to active as a product of being in the collider.
		if (relativePoint.x < -0.100) {
			ColliderLeft = true;
			AvatarIO.Somatosensory_L (true);
			Debug.Log("Got hit on the Left");
		} else if (relativePoint.x > 0.100) {
			ColliderRight = true;
			AvatarIO.Somatosensory_R (true);
			Debug.Log("Got hit on the Right");
		} else {
			ColliderLeft = true;
			ColliderRight = true;
			AvatarIO.Somatosensory_L (true);
			AvatarIO.Somatosensory_R (true);
			Debug.Log("Got hit on both sides");
		}

	}

}
