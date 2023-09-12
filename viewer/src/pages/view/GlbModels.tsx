import React, { useContext } from 'react'

import { guidContext } from './contexts' 

import { useGLTF } from '@react-three/drei'
import { Mesh, MeshStandardMaterial } from 'three'
import { GLTFResult } from 'innerDataModel/GltfResult';

const GlbModels: React.FC<{
    nodes: Object
    selectedClasses: string[]
   }> = (props) => {
    const ctx = useContext(guidContext)
    const handleClick = (guid: string) => {
        console.log(guid)
        //setShowDetail(false)
        ctx.setNewGuid(guid)
        //setClickPoint(e.point)
        //setShowDetail(true)
      }
    return (
        <>
        {Object.values(props.nodes).map((node: Mesh) =>
            props.selectedClasses.includes(node.userData.class_name) && 
            ( node.userData.global_id===ctx.guid
                ? <mesh
                        geometry={node.geometry}
                        material-color={"yellow"}
                        name={node.userData.global_id}
                        onDoubleClick={(e) => (e.stopPropagation(), (handleClick(node.userData.global_id)))}
                    />
                : <mesh
                        geometry={node.geometry}
                        material={node.material}
                        name={node.userData.global_id}
                        onDoubleClick={(e) => (e.stopPropagation(), (handleClick(node.userData.global_id)))}
                    />
            )
        )}
        </>
    )
}

export default GlbModels