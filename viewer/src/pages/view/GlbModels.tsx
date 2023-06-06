import React, { useContext } from 'react'

import { guidContext } from './contexts' 

import { useGLTF } from '@react-three/drei'
import { Mesh, MeshStandardMaterial } from 'three'
import { GLTF } from 'three/examples/jsm/loaders/GLTFLoader';

type GLTFResult = GLTF & {
    nodes: Object
    materials: {
        '': THREE.MeshStandardMaterial
    }
}

const GlbModels: React.FC<{
    modelId: string
   }> = (props) => {
    console.log(props.modelId)
    const ctx = useContext(guidContext)
    const { nodes } = useGLTF(`http://localhost:8000/v1/ifcgeometry/${props.modelId}.glb`) as GLTFResult
    const handleClick = (guid: string) => {
        console.log(guid)
        //setShowDetail(false)
        ctx.setNewGuid(guid)
        //setClickPoint(e.point)
        //setShowDetail(true)
      }
    return (
        <>
        {Object.values(nodes).map((node: Mesh) => 
            node.userData.global_id===ctx.guid
            ? <mesh
                    geometry={node.geometry}
                    material-color={"yellow"}
                    onDoubleClick={(e) => (e.stopPropagation(), (handleClick(node.userData.global_id)))}
                />
            : <mesh
                    geometry={node.geometry}
                    material={node.material}
                    onDoubleClick={(e) => (e.stopPropagation(), (handleClick(node.userData.global_id)))}
                />             
        )}
        </>
    )
}

// yellowじゃなくてblackになる理由を探す
// API経由でuseGLTFやる方法探す
// →glb対応完了
// clickFocus

export default GlbModels