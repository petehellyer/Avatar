// This code is for the LHS rendering, purely to allow you to fly about a bit. Press space to move forwards. This stuff has no effect on the model

using UnityEngine;
using System.Collections;

public class FlyAround : MonoBehaviour {
	public float moveSpeed = 50.0F;
	
	private float horizontalDirection;
	private float verticalDirection;
	public float stability = 0.3f;
	public float speed = 2.0f;
	public Vector3 predictedUp;
	public Vector3 torqueVector;
	void FixedUpdate() {
		
		horizontalDirection = Input.GetAxis ("Horizontal") * 100.0f * Time.deltaTime;// + rotation_preRotate.y;
		verticalDirection = Input.GetAxis ("Vertical") * 100.0f * Time.deltaTime;// + rotation_preRotate.y;
		transform.Rotate (verticalDirection, horizontalDirection, 0);
		predictedUp = Quaternion.AngleAxis (GetComponent <Rigidbody> ().angularVelocity.magnitude * Mathf.Rad2Deg * stability / speed, GetComponent <Rigidbody> ().angularVelocity) * transform.up;
		torqueVector = Vector3.Cross (predictedUp, Vector3.up);
		torqueVector = Vector3.Project (torqueVector, transform.forward);
		GetComponent <Rigidbody> ().AddTorque (torqueVector * speed * speed);
		if (Input.GetKey (KeyCode.Space)) {
			GetComponent<Rigidbody> ().AddRelativeForce (moveSpeed * Vector3.forward);
			
		}
	}
}

