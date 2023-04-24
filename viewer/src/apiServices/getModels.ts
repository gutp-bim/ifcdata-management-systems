import React, {useState, useEffect} from 'react';
import { MetaDataModel } from '../innerDataModel/MetaDataModel';

type RawMetaDataModel = {
    'ifcmodel_id': string,
    'model_name': string,
    'description': string,
    'schema_version': string
}

export const useGetModels: (() => MetaDataModel[]) = () => {
    const [posts, setPosts] = useState([])
    useEffect(() => {
        fetch(`http://localhost:8080/v1/ifcmodels`, {method: 'GET'})
        .then(res => res.json())
        .then(rawModels => {
            setPosts(rawModels.map((rawModel: RawMetaDataModel) => 
                MetaDataModel.make(
                    rawModel.ifcmodel_id,
                    rawModel.model_name,
                    rawModel.description,
                    rawModel.schema_version
                )
            ))
        })
    }, [])
    return posts
};
