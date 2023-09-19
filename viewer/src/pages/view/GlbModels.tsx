import React, { useContext, useState } from 'react'
import * as Reactstrap from "reactstrap"

import { guidContext } from './contexts' 
import { useGetInstanceDetail } from 'apiServices/getInstanceDetail';

import { Html } from "@react-three/drei";
import { Mesh, Vector3 } from 'three'

const GlbModels: React.FC<{
    nodes: Object
    selectedClasses: string[]
    modelId: string
   }> = (props) => {
    const ctx = useContext(guidContext)
    const [clickPoint, setClickPoint] = useState<Vector3>();
    const [showDetail, setShowDetail] = useState<boolean>(false);

    const handleClick = (guid: string, point: Vector3) => {
        setShowDetail(false)
        ctx.setNewGuid(guid)
        setClickPoint(point)
        setShowDetail(true)
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
                        onDoubleClick={(e) => (e.stopPropagation(), (handleClick(node.userData.global_id, e.point)))}
                    >
                        {(node.userData.global_id===ctx.guid && showDetail) &&
                            <Html
                                position={clickPoint}
                            >
                                <div className="detail-window">
                                    <DetailInfo modelId = {props.modelId} guid = {node.userData.global_id} />
                                    <Reactstrap.Button className="detail-close" onClick={() => setShowDetail(false)} style={{ userSelect: "none" }}>
                                    Close
                                    </Reactstrap.Button>
                                </div>
                            </Html>}
                    </mesh>
                : <mesh
                        geometry={node.geometry}
                        material={node.material}
                        name={node.userData.global_id}
                        onDoubleClick={(e) => (e.stopPropagation(), (handleClick(node.userData.global_id, e.point)))}
                    />
            )
        )}
        </>
    )
}

const DetailInfo: React.FC<{
    modelId: string,
    guid: string
}> = (props) => {
    const detail = useGetInstanceDetail(props.modelId, props.guid)
    switch (detail.status) {
      case 'loading':
        return (<div className="detail-body-load">Loading...</div>)
      case 'failure':
        return (<div className="detail-body">Data Not Available</div>)
      case 'success':
        return (
          <div className="detail-body">
            {
              [...detail.info.entries()].map(([k, v]) => {
                return (<div>{k}: {v}</div>)
              })
            }
          </div>
        )
    }
}

export default GlbModels