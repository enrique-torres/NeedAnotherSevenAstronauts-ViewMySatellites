using UnityEngine;
using System.Collections;

public class CameraMovement : MonoBehaviour
{
	// STATE
	private float _initialYAngle = 0f;
	private float _appliedGyroYAngle = 0f;
	private float _calibrationYAngle = 0f;
	private Transform _rawGyroRotation;
	private float _tempSmoothing;
	private Camera camera;
	private Vector3 oldPosition;

	// SETTINGS
	[SerializeField] private float _smoothing = 0.1f;

	// Zoom related variables
	public float perspectiveZoomSpeed = 0.2f;       // The rate of change of the field of view in perspective mode.
	private bool isFocusedOnSatellite = false;		// Indicates if we're focused on a satellite right now

	private IEnumerator Start()
	{
		camera = GetComponent<Camera>();
		Input.gyro.enabled = true;
		Application.targetFrameRate = 60;
		_initialYAngle = transform.eulerAngles.y;

		_rawGyroRotation = new GameObject("GyroRaw").transform;
		_rawGyroRotation.position = transform.position;
		_rawGyroRotation.rotation = transform.rotation;

		// Wait until gyro is active, then calibrate to reset starting rotation.
		yield return new WaitForSeconds(1);

		StartCoroutine(CalibrateYAngle());
	}

	private void Update()
	{
		ApplyGyroRotation();
		ApplyCalibration();

		transform.rotation = Quaternion.Slerp(transform.rotation, _rawGyroRotation.rotation, _smoothing);

		ZoomHandling();
	}

	private IEnumerator CalibrateYAngle()
	{
		_tempSmoothing = _smoothing;
		_smoothing = 1;
		_calibrationYAngle = _appliedGyroYAngle - _initialYAngle; // Offsets the y angle in case it wasn't 0 at edit time.
		yield return null;
		_smoothing = _tempSmoothing;
	}

	private void ApplyGyroRotation()
	{
		_rawGyroRotation.rotation = Input.gyro.attitude;
		_rawGyroRotation.Rotate(0f, 0f, 180f, Space.Self); // Swap "handedness" of quaternion from gyro.
		_rawGyroRotation.Rotate(90f, 180f, 0f, Space.World); // Rotate to make sense as a camera pointing out the back of your device.
		_appliedGyroYAngle = _rawGyroRotation.eulerAngles.y; // Save the angle around y axis for use in calibration.
	}

	private void ApplyCalibration()
	{
		_rawGyroRotation.Rotate(0f, -_calibrationYAngle, 0f, Space.World); // Rotates y angle back however much it deviated when calibrationYAngle was saved.
	}

	public void SetEnabled(bool value)
	{
		enabled = true;
		StartCoroutine(CalibrateYAngle());
	}

	private void ZoomHandling()
	{
		// If there are two touches on the device...
		if (Input.touchCount == 2 && !isFocusedOnSatellite)
		{
			// Store both touches.
			Touch touchZero = Input.GetTouch(0);
			Touch touchOne = Input.GetTouch(1);

			// Find the position in the previous frame of each touch.
			Vector2 touchZeroPrevPos = touchZero.position - touchZero.deltaPosition;
			Vector2 touchOnePrevPos = touchOne.position - touchOne.deltaPosition;

			// Find the magnitude of the vector (the distance) between the touches in each frame.
			float prevTouchDeltaMag = (touchZeroPrevPos - touchOnePrevPos).magnitude;
			float touchDeltaMag = (touchZero.position - touchOne.position).magnitude;

			// Find the difference in the distances between each frame.
			float deltaMagnitudeDiff = prevTouchDeltaMag - touchDeltaMag;

			// Otherwise change the field of view based on the change in distance between the touches.
			camera.fieldOfView += deltaMagnitudeDiff * perspectiveZoomSpeed;

			// Clamp the field of view to make sure it's between 0 and 180.
			camera.fieldOfView = Mathf.Clamp(camera.fieldOfView, 20f, 75f);
		}
	}

	public void ZoomOnSatellite(Transform sat)
	{
		isFocusedOnSatellite = true;
		oldPosition = this.transform.position;

	}
}
