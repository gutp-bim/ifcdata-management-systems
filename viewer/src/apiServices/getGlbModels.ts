import { GLTFResult } from 'innerDataModel/GltfResult';
import { useGLTF } from "@react-three/drei";

export const useGetGlbModels: ((modelId: string, lod: string | undefined) => Object) = (modelId: string, lod: string | undefined) => {
    const url = (typeof lod === "undefined" || lod === "3")
        ? `http://localhost:8000/v1/ifcgeometry/${modelId}-3.glb`
        : `http://localhost:8000/v1/ifcgeometry/${modelId}-${lod}.glb`
    const { nodes } = useGLTF(url) as GLTFResult
    return nodes
}