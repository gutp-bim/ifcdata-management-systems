import { useState, useEffect, Suspense } from 'react';
import Split from "react-split";
import { useParams } from "react-router-dom";

import { guidContext, useGuidContext } from './contexts'
import GlbModels from './GlbModels';
import TreeRow from './TreeView'
import SelectToZoom from './SelectToZoom';
import { Bounds } from './Bounds'
import { TreeNode } from 'innerDataModel/TreeNode';
import { getTreeData } from 'apiServices/getTreeData';
import { ModelViewPageProps } from "main/routes";

import { AssertionError } from "assert";
import { OrbitControls } from "@react-three/drei";
import { Canvas } from '@react-three/fiber';
import { EffectComposer, SSAO } from '@react-three/postprocessing';
import { BlendFunction } from "postprocessing";
import { BufferGeometry, BufferAttribute } from 'three';

import 'styles.css'
 
const View = () => {
  const { modelId, lod } = useParams<ModelViewPageProps>();
  if (modelId === undefined || modelId === null) {
    throw new AssertionError(
        {message: `Expected modelId to be defined, but received ${modelId}`}
    )
  }
  const [roots, setRoots] = useState<TreeNode[]>([])
  useEffect(() => {
    setRoots(getTreeData(modelId))
  }, [modelId])
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
          {roots.map((root) => (
            <TreeRow key={`${root.type}-${root.guid}`} node={root} level={0} />
          ))}
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
              frameloop="demand"
              camera={{position: [-3, 20, 0]}}
              >
              <Suspense fallback={null}>
                <Bounds fit clip margin={1.2} fixedOrientation>
                  <GlbModels modelId={modelId} lod={lod}/>
                  <SelectToZoom />
                </Bounds>
              </Suspense>
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