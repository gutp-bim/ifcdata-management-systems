import React, { useState, useContext } from 'react';
import * as Reactstrap from "reactstrap"

import { guidContext } from './contexts' 
import { useGetInstanceDetail } from 'apiServices/getInstanceDetail';

import { Html } from "@react-three/drei";
import { ThreeEvent } from '@react-three/fiber';
import { BufferGeometry, Vector3 } from 'three';

import 'styles.css'

const SingleElement: React.FC<{
    bufGeo: BufferGeometry,
    colors: number[],
    guid: string,
    modelId: string
   }> = (props) => {
    const [clickPoint, setClickPoint] = useState<Vector3>();
    const [showDetail, setShowDetail] = useState<boolean>(false);
    const ctx = useContext(guidContext)
    const isFocused = props.guid === ctx.guid
    const handleClick = (e: ThreeEvent<MouseEvent>) => {
      setShowDetail(false)
      e.stopPropagation()
      ctx.setNewGuid(props.guid)
      setClickPoint(e.point)
      setShowDetail(true)
    }
    return (
      <mesh 
        geometry={props.bufGeo}
        onDoubleClick={(e) => handleClick(e)}
      >
        {
          props.colors[3] === 1.0
            ? <meshStandardMaterial color={isFocused ? "yellow" : `rgb(${Math.round(props.colors[0] * 255)}, ${Math.round(props.colors[1] * 255)}, ${Math.round(props.colors[2] * 255)})`} />
            : <meshStandardMaterial color={isFocused ? "yellow" : `rgb(${Math.round(props.colors[0] * 255)}, ${Math.round(props.colors[1] * 255)}, ${Math.round(props.colors[2] * 255)})`} opacity={props.colors[3]} transparent />
        } 
        {(isFocused && showDetail) &&
          <Html
            position={clickPoint}
          >
            <div className="detail-window">
              <DetailInfo modelId = {props.modelId} guid = {props.guid} />
              <Reactstrap.Button className="detail-close" onClick={() => setShowDetail(false)} style={{ userSelect: "none" }}>
                Close
              </Reactstrap.Button>
            </div>
          </Html>}
      </mesh>
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

export default SingleElement