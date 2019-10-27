using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;
using TMPro;
using UnityEngine.EventSystems;
public class ClickDetection : MonoBehaviour
{
    public SatelliteManager satelliteManager;
    public GameObject menu;
    public GameObject selectedSat;
    public Text satName;
    public Text url;
    public Text uiSatName;
	public CameraMovement camMov;
    // Update is called once per frame
    void Update()
    {
        if (Input.touchCount > 0)
        {
            Touch touch = Input.GetTouch(0);

            if (touch.phase == TouchPhase.Began)
            {
                Ray ray = Camera.main.ScreenPointToRay(touch.position);
                RaycastHit hit;
                if (Physics.Raycast(ray, out hit)) {
                    selectedSat = hit.collider.gameObject;
                    try {
                        satName.text = selectedSat.GetComponent<SatelliteMono>().satname;
                        uiSatName.text = selectedSat.GetComponent<SatelliteMono>().satname;
                    }
                    catch (Exception ex) {
                        Debug.Log(ex.ToString());
                    }
                    try {
                        url.text = selectedSat.GetComponent<SatelliteMono>().url;
                    }
                    catch (Exception ex) {
                        Debug.Log(ex.ToString());
                    }                    
                    menu.SetActive(true);
                    Debug.Log("Hit a satellite");
                }
            }
        }
    }

    public void GoToSatellite() {
        menu.SetActive(false);
        satelliteManager.SatellitesToRealPos(selectedSat);
    }
}
