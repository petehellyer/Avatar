// This code Links the avatar to the computational model. Adapted from Standard Assets

using System;
using UnityEngine;

public class Motor : MonoBehaviour
{
	// Unity Hooks to Computational Model and the Actor.
	public AvatarInterop InteropObject;
	public float v;
	public float h;
	private float speed = 2; //move avatar 2 units per frame update
	public GameObject ColliderObject;

    private void FixedUpdate ()
    {
	    if (InteropObject.NextSimulation > InteropObject.StepSimulation)
	    {
		    // actually move the character
		    v = (float) InteropObject.Fwd;
		    h = (float) InteropObject.Rot;

		    CharacterController controller = GetComponent<CharacterController>();
		    
//		    // For testing purpose move the avatar with arrows
//		    Vector3 move = new Vector3(0, 0, Input.GetAxis("Vertical")*5);
//		    // transforms move from local space to world space
//		    move = transform.TransformDirection(move);
//		    GetComponent<Transform>().Rotate(0, Input.GetAxis("Horizontal")*10, 0);
//		    controller.Move(move * Time.deltaTime * speed);
//		    Debug.Log(transform.position);
		    
		    Vector3 move = new Vector3(0, 0, v);
		    // transforms move from local space to world space. This allows the avatar to move in
		    // the direction it is facing
		    move = transform.TransformDirection(move);
		    GetComponent<Transform>().Rotate(0, h, 0);
		    // move avatar
		    controller.Move(move * Time.deltaTime * speed);
		    
		    // The Avatar should not move on the y position
		    Vector3 currentPos = transform.position;
		    currentPos.y = 1000;
		    transform.position = currentPos;
			// Send the current position to Python
		    InteropObject.client.SendPosition(transform.position.z, transform.position.x);
		    
			InteropObject.client.SendNextUnityCondition(true);
			// Debug.Log("Finished Unity simulation " + InteropObject.StepSimulation);
			InteropObject.StepSimulation = InteropObject.NextSimulation;

	    }
    }

//	private void OnControllerColliderHit(ControllerColliderHit hit)
//	{
//		Debug.Log("I hit something");
//	}
}
