using System.Collections;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using Assets.SimpleAndroidNotifications;
using TMPro;
using System;
public class SatelliteManager : MonoBehaviour
{
	//Server communication variables
	string server_ip = "http://35.180.254.56:80/GiveMe?";
	float timeBetweenRequests = 1f;

	//Satellites related variables
    List<Satellite> sats = new List<Satellite>();
    Dictionary<string,GameObject> satObjects = new Dictionary<string, GameObject>();
	public GameObject[] satellite_models;
	public GameObject loading_screen;
	GameObject currentSat = null;
	public Text uiSatName;

	//User and non satellite entities related variables
	public GameObject earthObject;
    public Vector3 oldCamPosition;
    float lon = 0.0f, lat = 0.0f, alt = 0.0f;
    public Transform userPosition;
	public GameObject sun;

	//UI and synchronization related variables
	public GameObject backButton;
    bool isStarting = true;
    

	//Start method that runs when the object is loaded. It loads the location of the user and
	//calls the coroutines to load in the satellites
    IEnumerator Start()
    {
        Debug.Log("Getting location");
        // First, check if user has location service enabled
        if (!Input.location.isEnabledByUser)
            yield break;

        // Start service before querying location
        Input.location.Start();

        // Wait until service initializes
        int maxWait = 20;
        while (Input.location.status == LocationServiceStatus.Initializing && maxWait > 0)
        {
            yield return new WaitForSeconds(1);
            maxWait--;
        }

        // Service didn't initialize in 20 seconds
        if (maxWait < 1)
        {
            NotificationManager.Send(System.TimeSpan.FromSeconds(0), "Error de ubicacion", "Timeout en ubicacion", Color.black, NotificationIcon.Bell);
            Application.Quit();
            yield break;
        }

        // Connection has failed
        if (Input.location.status == LocationServiceStatus.Failed)
        {
            
            print("Unable to determine device location");
            NotificationManager.Send(System.TimeSpan.FromSeconds(0), "Error de ubicacion", "No se pudo determinar la ubicacion", Color.black, NotificationIcon.Bell);
            Application.Quit();
            yield break;
        }
        else
        {
            // Access granted and location value could be retrieved
            lon = Input.location.lastData.longitude;
            lat = Input.location.lastData.latitude;
            alt = Input.location.lastData.altitude;
        }
        // Stop service if there is no need to query location updates continuously
        Input.location.Stop();
        StartCoroutine(Upload());
        StartCoroutine(UpdateSatellites());
        yield return null;
    }

	//Uploads the user location to the server via a REST API call and downloads the satellite info
    IEnumerator Upload()
    {
        Debug.Log("Downloading data");

        UnityWebRequest www = UnityWebRequest.Get(server_ip + "lat=" + lat.ToString() + "&lon=" + lon.ToString() + "&alt=" + alt.ToString());
        yield return www.SendWebRequest();

        if (www.isNetworkError || www.isHttpError)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Form upload complete!");
        }

        int maxTries = 5;
        while (!www.isDone && maxTries > 0) {
            yield return new WaitForSeconds(1);
        }
        string json = www.downloadHandler.text;
        Debug.Log(json);
        ResponseInfo ri = JsonUtility.FromJson<ResponseInfo>(json);
        sun.transform.position = new Vector3(ri.sun_x, ri.sun_y, ri.sun_z);
        sun.transform.LookAt(earthObject.transform);

        foreach (Satellite s in ri.satellites) {
            sats.Add(s);
        }
        
        userPosition.position = new Vector3(ri.x, ri.y, ri.z);
        PlaceSatellites();
        isStarting = false;
    }

	//Places the satellites in 3D space around the user
    void PlaceSatellites() {
        GameObject satObj;
        foreach (Satellite s in sats) {
            int index = 0;
            Debug.Log(s.ToString());
            if (s.satname.Contains("GALILEO")) {
                index = 1;
            }
            else if (s.satname.Contains("ISS (ZARYA)")) {
                index = 2;
            }
            satObj = Instantiate(satellite_models[index], new Vector3(s.x, s.y, s.z), Quaternion.Euler(UnityEngine.Random.Range(0.0f, 360.0f), UnityEngine.Random.Range(0.0f, 360.0f), UnityEngine.Random.Range(0.0f, 360.0f)));
            SatelliteMono new_sat_values = satObj.GetComponent<SatelliteMono>();
            if (new_sat_values != null) {
                new_sat_values.satname = s.satname;
                new_sat_values.url = s.url;
                new_sat_values.x = s.x;
                new_sat_values.y = s.y;
                new_sat_values.z = s.z;
                new_sat_values.real_x = s.real_x;
                new_sat_values.real_y = s.real_y;
                new_sat_values.real_z = s.real_z;
                try {
                    satObjects.Add(s.satname,satObj);
                }
                catch(Exception ex) {
                    Debug.LogWarning(ex.ToString());
                }
            }
            else {
                Debug.LogWarning("Null new_sat");
                Debug.LogWarning(satObj.ToString());
            }
        }
        loading_screen.SetActive(false);
    }

	//When jumping to a satellite, it translates the satellite from the unitary sphere around
	//the user (done to better visualize all the satellites) and places it at it's real coordinates in space
    public void SatellitesToRealPos(GameObject cameraPos) {
        Vector3 new_pos = cameraPos.transform.position;
        float distance_to_earth = (earthObject.transform.position - new_pos).magnitude;
        if (distance_to_earth > 10000) {
            distance_to_earth = 10000;
        }
        foreach (KeyValuePair<string, GameObject> s in satObjects)
        {
            SatelliteMono s_info = s.Value.GetComponent<SatelliteMono>();
            Vector3 pos = new Vector3(s_info.real_x, s_info.real_y, s_info.real_z);
            s.Value.transform.position = pos;
            if ((pos - new_pos).magnitude > distance_to_earth) {
                s.Value.SetActive(false);
            }
        }
        oldCamPosition = Camera.main.transform.position;
        Camera.main.transform.position = cameraPos.transform.position;
        Vector3 lookAtModifier = Camera.main.transform.position;
        lookAtModifier = lookAtModifier + (lookAtModifier.normalized * 10);
        Camera.main.transform.position = lookAtModifier;
        Camera.main.transform.LookAt(earthObject.transform);
        earthObject.SetActive(true);
        currentSat = cameraPos;
        backButton.SetActive(true);
        uiSatName.gameObject.SetActive(true);
        StartCoroutine(HyperSpeedEffect());
    }
    
	//Inverse function to SatellitesToRealPos. This function translates the satellites from their real
	//space coordinates, into unitary sphere coordinates around the user location
    public void SatellitesToNormPos() {
        uiSatName.gameObject.SetActive(false);
        foreach (KeyValuePair<string, GameObject> s in satObjects)
        {
            SatelliteMono s_info = s.Value.GetComponent<SatelliteMono>();
            Vector3 pos = new Vector3(s_info.x, s_info.y, s_info.z);
            s.Value.transform.position = pos;
        }
        earthObject.SetActive(false);
        Camera.main.transform.position = oldCamPosition;
        currentSat = null;
        backButton.SetActive(false);
        StartCoroutine(HyperSpeedEffect());
    }

	//Coroutine that updates periodically the satellites positions
    IEnumerator UpdateSatellites() {
        while (isStarting) {
            yield return new WaitForSeconds(0.1f);
        }
        while (true) {
            yield return new WaitForSeconds(60);
            UnityWebRequest www = UnityWebRequest.Get(server_ip + "lat=" + lat.ToString() + "&lon=" + lon.ToString() + "&alt=" + alt.ToString());
            yield return www.SendWebRequest();

            if (www.isNetworkError || www.isHttpError)
            {
                Debug.Log(www.error);
            }
            else
            {
                Debug.Log("Form upload complete!");
            }

            int maxTries = 5;
            while (!www.isDone && maxTries > 0) {
                yield return new WaitForSeconds(1);
            }
            string json = www.downloadHandler.text;
            Debug.Log(json);
            ResponseInfo ri = JsonUtility.FromJson<ResponseInfo>(json);
            sun.transform.position = new Vector3(ri.sun_x, ri.sun_y, ri.sun_z);
            sun.transform.LookAt(earthObject.transform);

            foreach (Satellite s in ri.satellites) {
                SatelliteMono sm = satObjects[s.satname].GetComponent<SatelliteMono>();
                sm.x = s.x;
                sm.y = s.y;
                sm.z = s.z;
                sm.real_x = s.x;
                sm.real_y = s.y;
                sm.z = s.z;
                if (currentSat == null) {
                    satObjects[s.satname].transform.position = new Vector3(s.x, s.y, s.z);
                }
                else {
                    satObjects[s.satname].transform.position = new Vector3(s.real_x, s.real_y, s.real_z);
                }
            }
            if (currentSat != null) {
                currentSat = satObjects[currentSat.GetComponent<SatelliteMono>().satname];
                Camera.main.transform.position = currentSat.transform.position;
                Vector3 lookAtModifier = Camera.main.transform.position;
                lookAtModifier = lookAtModifier + (lookAtModifier.normalized * 10);
                Camera.main.transform.position = lookAtModifier;
            }
        }
    }

	public void SetAllSatellitesActiveState(bool active)
	{
		foreach (KeyValuePair<string, GameObject> s in satObjects)
		{
			s.Value.SetActive(active);
		}
	}

    public IEnumerator HyperSpeedEffect() {
		int warpTime = 10;
        while (warpTime >  0) {
            if (warpTime * 0.1f > 0.5f) {
                Camera.main.fieldOfView += 57f;
            }
            else {
                Camera.main.fieldOfView -= 57f;
            }
            warpTime--;
            yield return new WaitForSeconds(0.1f);
        }
        Camera.main.fieldOfView = 75f;
		if (currentSat == null)
		{
			SetAllSatellitesActiveState(true);
		}
		yield return null;
    }
}



