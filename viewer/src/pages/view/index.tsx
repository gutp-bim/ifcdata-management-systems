import { useState, useEffect, useMemo, Suspense } from 'react';
import Split from "react-split";
import { useParams } from "react-router-dom";

import { guidContext, useGuidContext } from './contexts'
import GlbModels from './GlbModels';
import TreeRow from './TreeView'
import Plane from './Plane'
import SelectToZoom from './SelectToZoom';
import { Bounds } from './Bounds'
import { TreeNode } from 'innerDataModel/TreeNode';
import { getTreeData } from 'apiServices/getTreeData';
import { getGlbModels } from 'apiServices/getGlbModels';
import { ModelViewPageProps } from "main/routes";

import { AssertionError } from "assert";
import { OrbitControls } from "@react-three/drei";
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
  const nodes = getGlbModels(modelId, lod)
  const [roots, setRoots] = useState<TreeNode[]>([])
  useEffect(() => {
    setRoots(getTreeData(modelId))
  }, [modelId])
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
  const [planeHeight, setPlaneHeight] = useState<number>(1.5)
  const [useSAO, setUseSAO] = useState("no-effect")
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
          <div>
            <select name="effect" onChange={(e) => setUseSAO(e.target.value)}>
              <option value="no-effect" selected>SAOなし</option>
              <option value="with-effect">SAOあり</option>
            </select>
          </div>
          <div style={{ width: `${window.innerWidth}`, height: `${window.innerHeight}px`}}>
            <Canvas
              gl={{ localClippingEnabled: true }}
              frameloop="demand"
              camera={{position: [-3, 20, 0]}}
              >
              <Suspense fallback={null}>
                <Bounds fit clip margin={1.2} fixedOrientation>
                  <GlbModels nodes={nodes} selectedClasses={selectedClasses} boudingBoxes={boudingBoxes} planeHeight={planeHeight} modelId={modelId}/>
                  <SelectToZoom />
                </Bounds>
              </Suspense>
              <Plane planeHeight={planeHeight} setPlaneHeight={setPlaneHeight} boudingBoxes={boudingBoxes} />
              <OrbitControls makeDefault />
              <ambientLight />
              <pointLight position={[10, 10, 10]} />
              {
                useSAO === "with-effect"
                ? (              
                <EffectComposer>
                  <SSAO 
                    blendFunction={BlendFunction.MULTIPLY}
                    samples={31}
                    radius={5}
                    intensity={30}
                  />
                </EffectComposer>)
                : <></>
              }

            </Canvas>
          </div>
        </Split>
      </Split>
    </guidContext.Provider>
  );
}

export default View;