import React, {useState, useEffect} from 'react';
import { ElementDetailResponse } from 'innerDataModel/ElementDetail';

type ValueType = 'string' | 'reference' | 'null'

type AttributeValue = {
    'value': {
        'value_type': ValueType,
        'value': string
    },
    'attribute_name': string
}

export const useGetInstanceDetail: ((modelId: string, guid: string) => ElementDetailResponse) = (modelId: string, guid: string) => {
    const [posts, setPosts] = useState<ElementDetailResponse>(ElementDetailResponse.loading());
    useEffect(() => {
        fetch(`http://localhost:8080/v1/ifcinstance/${modelId}/${guid}`, {method: 'GET'})
        .then(res => res.json())
        .then(async data => {
            const infoWithoutRef = await Promise.all(data['attribute_values'].map(async (e: AttributeValue) => {
                if (e['value']['value_type'] == 'reference') {
                    const referenceName = await getSingleName(modelId, e['value']['value'])
                    return [e['attribute_name'], referenceName]
                } else {
                    return [e['attribute_name'], e['value']['value']]
                } 
        }))
            setPosts(ElementDetailResponse.success(new Map(infoWithoutRef)))
        })
        .catch((err) => {
            setPosts(ElementDetailResponse.failure())
        }
        )
    }, [])
    console.log(posts)
    return posts
};

const getSingleName = (modelId: string, guid: string) => {
    const result = fetch(`http://localhost:8080/v1/ifcinstance/${modelId}/${guid}`, {method: 'GET'})
        .then(res => {
            if (!res.ok) {
                throw new Error(res.statusText)
            }
            return res.json()
        })
        .then(data => data['attribute_values'].find((el: AttributeValue) => el['attribute_name'] == 'Name')['value']['value'])
        .catch((err) => 'Data Not Available')
    return result
}
