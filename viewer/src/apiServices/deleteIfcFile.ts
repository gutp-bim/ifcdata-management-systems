export const deleteToModelServer = async (modelId: string) => {
    const response = await fetch(
        `http://localhost:8080/v1/ifcmodel/${modelId}`,{method: 'DELETE'}
    )
    return response.json()
}

export const deleteToGeometryServer = async (modelId: string) => {
    const response = await fetch(
        `http://localhost:8080/v1/ifcgeometry/${modelId}`,{method: 'DELETE'}
    )
    return response.json()
}