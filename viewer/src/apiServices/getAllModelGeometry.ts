import React, {useState, useEffect} from 'react';
import data from '../apiout_all.json';
import { Geometry } from 'innerDataModel/Geometry';

export const getAllModelGeometry: ((modelId: string) => Geometry[]) = (modelId: string) => {
    /*
    const [posts, setPosts] = useState([])
    useEffect(() => {
        fetch(s'http://52.185.188.169:8080/v1/ifcmodels/${modelId}', {method: 'GET'})
        .then(res => res.json())
        .then(data => {
            setPosts(data)
        })
    }, [])

    return MetaDataModel.fromJson(data)
    */
   const all_geos =data.geometries
   if (modelId == "5025f9163e4b4bf4a70afd46ee5d445d") {
    return [{
        guid: "5025f9163e4b4bf4a70afd46ee5d445d",
        faceColors: [],
        vertices: [],
        indices: []
    }]
   } else {
    return all_geos.map((geo) => Geometry.make(
        geo.globally_unique_id,
        geo.face_colors,
        geo.vertices,
        geo.indices
    ))
   }
}
