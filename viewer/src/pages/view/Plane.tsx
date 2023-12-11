import React, { useState, useMemo } from 'react'
import { Box3 } from 'three'
import { ThreeEvent, useThree } from '@react-three/fiber';
import { TransformControls } from "@react-three/drei";

const Plane: React.FC<{
    clippingMode: string,
    planeHeight: number,
    setPlaneHeight: React.Dispatch<React.SetStateAction<number>>,
    boudingBoxes: Map<string, Box3 | null>,
}> = (props) => {
    const initialPlaneHeight = props.planeHeight
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
                props.clippingMode==='no-clipping'
                    ? <></>
                    : <>
                        {
                            isPlaneFocused
                            && <TransformControls
                                object={planeObj}
                                mode='translate'
                                showX={false}
                                showY={false}
                                onMouseUp={(e) => {
                                    props.setPlaneHeight(props.planeHeight + e?.target.offset.z)
                                }}
                                />
                        }
                        <mesh
                            name='plane'
                            position={[(edges[0]+edges[1])/2,(edges[2]+edges[3])/2,initialPlaneHeight]}
                            onDoubleClick={(e: ThreeEvent<MouseEvent>) => {
                                e.stopPropagation()
                                setIsPlaneFocused(true)
                            }}
                            onPointerMissed={(e) => e.type === 'click' && setIsPlaneFocused(false)}
                        >
                            <planeGeometry args={[(edges[1]-edges[0])+20,(edges[3]-edges[2])+20]}/>
                            <meshStandardMaterial transparent opacity={isPlaneFocused ? 0.4 : 0.2}/>
                        </mesh>
                    </>
            }
      </>
    )
}

export default Plane