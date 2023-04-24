export const postToModelServer = async (file: File, name: string, description: string) => {
    const formData = new FormData()
    formData.append('upfile', file)
    formData.append('modelname', name)
    formData.append('description', description)
    const response = await fetch(
        'http://localhost:8080/v1/ifcmodel',
        {
            method: 'POST',
            body: formData
        }
    )
    return response.json()
};

export const postToGeometryServer = async (file: File, id: string) => {
    const formData = new FormData()
    formData.append('upfile', file)
    formData.append('ifcmodel_id', id)
    const response = await fetch(
        'http://localhost:8000/v1/ifcgeometry/upload',
        {
            method: 'POST',
            body: formData
        }
    )
    return response.json()
}