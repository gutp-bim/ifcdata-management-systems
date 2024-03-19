import React, { useState, useMemo } from 'react'
import { Box3 } from 'three'
import { ThreeEvent, useThree } from '@react-three/fiber';
import { TransformControls } from "@react-three/drei";

import { ClippingMode } from './ClippingMode';

const Plane: React.FC<{
    clippingMode: ClippingMode,
    planePosition: number,
    setPlanePosition: React.Dispatch<React.SetStateAction<number>>,
    boudingBoxes: Map<string, Box3 | null>,
}> = (props) => {
    const clippingMode = props.clippingMode
    const initialPlanePosition = props.planePosition
    const [isPlaneFocused, setIsPlaneFocused] = useState(false)
    
    const edges = useMemo(() => [
        Math.min(...Array.from(props.boudingBoxes.values()).map(v => v?.min.x).filter((v): v is number => v!=null)),
        Math.max(...Array.from(props.boudingBoxes.values()).map(v => v?.max.x).filter((v): v is number => v!=null)),
        Math.min(...Array.from(props.boudingBoxes.values()).map(v => v?.min.y).filter((v): v is number => v!=null)),
        Math.max(...Array.from(props.boudingBoxes.values()).map(v => v?.max.y).filter((v): v is number => v!=null)),
        Math.min(...Array.from(props.boudingBoxes.values()).map(v => v?.min.z).filter((v): v is number => v!=null)),
        Math.max(...Array.from(props.boudingBoxes.values()).map(v => v?.max.z).filter((v): v is number => v!=null))
    ], [props.boudingBoxes])

    const { scene } = useThree()
    const planeObj = scene.getObjectByName('plane')
    return (
        <>
            {
                clippingMode.enableClip===false
                    ? <></>
                    : <>
                        {
                            isPlaneFocused
                            && <TransformControls
                                object={planeObj}
                                mode='translate'
                                showX={clippingMode.axis==='x' ? true : false}
                                showY={clippingMode.axis==='y' ? true : false}
                                showZ={clippingMode.axis==='z' ? true : false}
                                onMouseUp={(e) => {
                                    props.setPlanePosition(props.planePosition + e?.target.offset?.[clippingMode.axis])
                                }}
                                />
                        }
                        <mesh
                            name='plane'
                            position={
                                clippingMode.axis==='x'
                                ? [initialPlanePosition,(edges[2]+edges[3])/2,(edges[4]+edges[5])/2]
                                : clippingMode.axis==='y'
                                    ? [(edges[0]+edges[1])/2,initialPlanePosition,(edges[4]+edges[5])/2]
                                    : [(edges[0]+edges[1])/2,(edges[2]+edges[3])/2,initialPlanePosition]
                            }
                            rotation={
                                clippingMode.axis==='x'
                                ? [0,Math.PI/2,0]
                                : clippingMode.axis==='y'
                                    ? [Math.PI/2,0,0]
                                    : [0,0,0]
                            }
                            onDoubleClick={(e: ThreeEvent<MouseEvent>) => {
                                e.stopPropagation()
                                setIsPlaneFocused(true)
                            }}
                            onPointerMissed={(e) => e.type === 'click' && setIsPlaneFocused(false)}
                        >
                            <planeGeometry args={
                                clippingMode.axis==='x'
                                ? [(edges[5]-edges[4])+20,(edges[3]-edges[2])+20]
                                : clippingMode.axis==='y'
                                    ? [(edges[1]-edges[0])+20,(edges[5]-edges[4])+20]
                                    : [(edges[1]-edges[0])+20,(edges[3]-edges[2])+20]
                            }
                            />
                            <meshStandardMaterial transparent opacity={isPlaneFocused ? 0.4 : 0.2}/>
                        </mesh>
                    </>
            }
      </>
    )
}

export default Plane