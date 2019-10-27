using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

[Serializable]
public class ResponseInfo 
{
    public float x, y, z, sun_x, sun_y, sun_z;
    public List<Satellite> satellites = new List<Satellite>();
}
