import { useState, useEffect, useMemo, Suspense } from 'react';
import Split from "react-split";
import { useParams } from "react-router-dom";

import { guidContext, useGuidContext } from './contexts'
import GlbModels from './GlbModels';
import TreeRow from './TreeView'
import Plane from './Plane'
import SelectToZoom from './SelectToZoom';
import { Bounds } from './Bounds'
import { ClippingMode, clippingModeOptions } from './ClippingMode';
import { TreeNode } from 'innerDataModel/TreeNode';
import { useGetTreeData } from 'apiServices/getTreeData';
import { useGetGlbModels } from 'apiServices/getGlbModels';
import { ModelViewPageProps } from "main/routes";

import { AssertionError } from "assert";
import { OrbitControls, PerspectiveCamera, OrthographicCamera } from "@react-three/drei";
import { Canvas } from '@react-three/fiber';
import { EffectComposer, SSAO } from '@react-three/postprocessing';
import { BlendFunction } from "postprocessing";
import { Mesh, BufferGeometry, Box3 } from 'three';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';

import 'styles.css'
import 'react-tabs/style/react-tabs.css';
 
const View = () => {
  const { modelId, lod } = useParams<ModelViewPageProps>();
  if (modelId === undefined || modelId === null) {
    throw new AssertionError(
        {message: `Expected modelId to be defined, but received ${modelId}`}
    )
  }
  const nodes = useGetGlbModels(modelId, lod)
  const roots = useGetTreeData(modelId)
  const boudingBoxes: Map<string, Box3 | null> = useMemo(() => {
    const map = new Map();
    for (const node of Object.values(nodes)) {
      if (node.type !== 'Mesh') continue
      const geom: BufferGeometry = node.geometry
      geom.computeBoundingBox()
      map.set(node.userData.global_id, geom.boundingBox)
    }
    return map
  }, [nodes])
  const classNames = Array.from(new Set(Object.values(nodes).map((node: Mesh) => node.userData.class_name))).filter(el => typeof el !== "undefined")
  const [selectedClasses, setSelectedClasses] = useState(classNames)
  const [effectMode, setEffectMode] = useState("no-effect")
  const [cameraMode, setCameraMode] = useState("perspective")
  const [clippingMode, setClippingMode] = useState<ClippingMode>(ClippingMode.noClip())
  const [planePosition, setPlanePosition] = useState<number>(1.5)
  const ctx = useGuidContext();
  
  return (
    <guidContext.Provider value={ctx}>
      <Split
        className="flex"
        gutter={() => {
          const gutterElement = document.createElement("div");
          gutterElement.className = `w-[2px] bg-indigo-500 hover:cursor-col-resize hover:w-4 hover:bg-indigo-700 transition-all delay-300 duration-300 ease-in-out`;
          return gutterElement;
        }}
        gutterStyle={() => ({})}
        sizes={[25, 75]}     
      >
        <div style={{ height: `${window.innerHeight}px`, overflow: "scroll"}}>
          <Tabs>
            <TabList>
              <Tab>ツリービュー</Tab>
              <Tab>IFCクラス</Tab>
            </TabList>
            <TabPanel>
              {roots.map((root) => (
                <TreeRow key={`${root.type}-${root.guid}`} node={root} level={0} />
              ))}
            </TabPanel>
            <TabPanel>
              {classNames.map((className) => (
                <p>
                <label>
                  <input
                    type="checkbox"
                    value={className}
                    checked={selectedClasses.includes(className)}
                    onChange={(e) => {
                      if (selectedClasses.includes(e.target.value)) {
                        setSelectedClasses(
                          selectedClasses.filter((selectedClasses) => selectedClasses !== e.target.value)
                        )
                      } else {
                        setSelectedClasses([...selectedClasses, e.target.value])
                      }
                    }}
                  />
                  {className}
                </label>
                </p>
              ))}
            </TabPanel>
          </Tabs>

        </div>
        <Split
          className="flex-vertical"
          sizes={[5, 95]}
          minSize={[10, 100]}
          direction="vertical"
        >
          <div style={{position: "relative"}}>
            <div style={{ width: `${window.innerWidth}`, height: `${window.innerHeight}px`}}>
              <Canvas
                gl={{ localClippingEnabled: true }}
                frameloop="demand"
                camera={{position: [-3, 10, 50]}}
                >
                  <PerspectiveCamera position={[-3, 10, 50]} makeDefault={cameraMode==="perspective"} />
                  <OrthographicCamera position={[-3, 10, 50]} makeDefault={cameraMode==="ortho"} />
                <Suspense fallback={null}>
                  <Bounds fit clip margin={1.2} fixedOrientation>
                    <GlbModels nodes={nodes} selectedClasses={selectedClasses} boudingBoxes={boudingBoxes} clippingMode={clippingMode} planePosition={planePosition} modelId={modelId}/>
                    <SelectToZoom />
                  </Bounds>
                </Suspense>
                <Plane clippingMode={clippingMode} planePosition={planePosition} setPlanePosition={setPlanePosition} boudingBoxes={boudingBoxes} />
                <OrbitControls makeDefault />
                <ambientLight />
                {
                  effectMode === "sao"
                  && (              
                  <EffectComposer>
                    <SSAO 
                      blendFunction={BlendFunction.MULTIPLY}
                      samples={31}
                      radius={5}
                      intensity={30}
                    />
                  </EffectComposer>)
                }

              </Canvas>
            </div>
            <div style={{position: "absolute", top: 0, left: 0, userSelect: "none"}}>
              <select name="effect" onChange={(e) => setEffectMode(e.target.value)} value={effectMode}>
                <option value="no-effect">SAOなし</option>
                <option value="sao">SAOあり</option>
              </select>
            </div>
            <div style={{position: "absolute", top: 0, left: 100, userSelect: "none"}}>
              <select name="clipping" onChange={(e) => setClippingMode(ClippingMode.fromString(e.target.value))} value={clippingMode.toString()}>
                {clippingModeOptions.map((op, idx) => (
                  <option key={idx} value={op.value}>{op.label}</option>
                ))}
              </select>
            </div>
            <div style={{position: "absolute", top: 0, left: 250, userSelect: "none"}}>
              <select name="camera" onChange={(e) => setCameraMode(e.target.value)} value={cameraMode}>
                <option value="perspective">パースペクティブカメラ</option>
                <option value="ortho">オルソカメラ</option>
              </select>
            </div>
          </div>
        </Split>
      </Split>
    </guidContext.Provider>
  );
}

export default View;