using System;
using UnityEngine;
using TMPro;
using UnityEngine.UI;
public class OpenHyperlinks : MonoBehaviour{
    public void OnClicked(Text text) {
        Application.OpenURL(text.text);
    }
}
