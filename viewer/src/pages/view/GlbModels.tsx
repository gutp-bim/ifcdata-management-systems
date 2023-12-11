import React, { useContext, useMemo, useState } from 'react'
import * as Reactstrap from "reactstrap"

import { guidContext } from './contexts' 
import { useGetInstanceDetail } from 'apiServices/getInstanceDetail';

import { Html } from "@react-three/drei";
import { BufferGeometry, Mesh, Vector3, Plane, Material, Box3 } from 'three'

const GlbModels: React.FC<{
    nodes: Object
    selectedClasses: string[],
    boudingBoxes: Map<string, Box3 | null>,
    clippingMode: string,
    planeHeight: number,
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
    const clipHeight = props.planeHeight
    const clipPlanes = useMemo(() => {
      return [new Plane(new Vector3(0,0, -1), clipHeight)]
    }, [clipHeight])

    return (
        <>
        {
          props.clippingMode==='no-clipping'
            ? (<> 
              {Object.values(props.nodes).map((node: Mesh) => {
                if (node.type !== 'Mesh') return (<></>)
                let material: Material | Material[] = []
                if (Array.isArray(node.material)) {
                  material = node.material.map((mat: Material) => {
                    mat.clippingPlanes = []
                    return mat
                  })
                } else {
                  const mat = node.material
                  mat.clippingPlanes = []
                  material = mat
                }
                return ((props.selectedClasses).includes(node.userData.class_name))
                  && (
                    (node.userData.global_id===ctx.guid)
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
              })}
            </>)
            : (<> 
              {Object.values(props.nodes).map((node: Mesh) => {
                if (node.type !== 'Mesh') return (<></>)
                let material: Material | Material[] = []
                if (Array.isArray(node.material)) {
                  material = node.material.map((mat: Material) => {
                    mat.clippingPlanes = clipPlanes
                    return mat
                  })
                } else {
                  const mat = node.material
                  mat.clippingPlanes = clipPlanes
                  material = mat
                }
                const boudingBoxEdge = props.boudingBoxes.get(node.userData.global_id)?.min?.z
                return (
                  <>
                  {((typeof boudingBoxEdge !== 'undefined' && boudingBoxEdge <= clipHeight) && (props.selectedClasses).includes(node.userData.class_name))
                  && <mesh
                    geometry={node.geometry}
                    material={material}
                    name={node.userData.global_id}
                  ></mesh>}
                  </>
                )
                })}
            </>)
        }
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