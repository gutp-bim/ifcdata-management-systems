import { GLTFResult } from 'innerDataModel/GltfResult';
import { useGLTF } from "@react-three/drei";
import { MeshStandardMaterial } from 'three'

export const useGetGlbModels: ((modelId: string, lod: string | undefined) => Object) = (modelId: string, lod: string | undefined) => {
    const url = (typeof lod === "undefined" || lod === "3")
        ? `http://localhost:8000/v1/ifcgeometry/${modelId}-3.glb`
        : `http://localhost:8000/v1/ifcgeometry/${modelId}-${lod}.glb`
    const { nodes } = useGLTF(url) as GLTFResult
    const materialUpdatedNodes = Object.fromEntries(
        Object.entries(nodes).map(([key, node]) => {
            if (node.type !== 'Mesh') { return [key, node] }
            if (node.material.type === 'MeshStandardMaterial') {
                const newMaterial: MeshStandardMaterial = node.material
                newMaterial.metalness = 0
                node.material = newMaterial
            }
            return [key, node]
        })
    )
    return materialUpdatedNodes
}