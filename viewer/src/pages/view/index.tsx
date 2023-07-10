import { useState, useEffect, Suspense } from 'react';
import Split from "react-split";
import { useParams } from "react-router-dom";

import { guidContext, useGuidContext } from './contexts'
import SingleElement from './ThreeDView'
import GlbModels from './GlbModels';
import TreeRow from './TreeView'
import SelectToZoom from './SelectToZoom';
import { Bounds } from './Bounds'
import { Geometry } from 'innerDataModel/Geometry';
import { TreeNode } from 'innerDataModel/TreeNode';
import { getTreeData } from 'apiServices/getTreeData';
import { getAllModelGeometry } from 'apiServices/getAllModelGeometry';
import { ModelViewPageProps } from "main/routes";

import { AssertionError } from "assert";
import { OrbitControls } from "@react-three/drei";
import { Canvas } from '@react-three/fiber';
import { EffectComposer, SSAO } from '@react-three/postprocessing';
import { BlendFunction } from "postprocessing";
import { BufferGeometry, BufferAttribute } from 'three';
import { mergeBufferGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils';

import 'styles.css'

const createGeometryByMaterialMap = (geo: Geometry) => {
    const geometryByMaterialMap = new Map<String, BufferGeometry[]>();
    for (let i = 0; i < geo.faceColors.length; i++) {
        const colId = `${geo.faceColors[i][0]}-${geo.faceColors[i][1]}-${geo.faceColors[i][2]}-${geo.faceColors[i][3]}`
        const geometry = new BufferGeometry();
        const vertices = new Float32Array([
            geo.vertices[3*geo.indices[3*i]], geo.vertices[3*geo.indices[3*i]+1], geo.vertices[3*geo.indices[3*i]+2],
            geo.vertices[3*geo.indices[3*i+1]], geo.vertices[3*geo.indices[3*i+1]+1], geo.vertices[3*geo.indices[3*i+1]+2],
            geo.vertices[3*geo.indices[3*i+2]], geo.vertices[3*geo.indices[3*i+2]+1], geo.vertices[3*geo.indices[3*i+2]+2]
        ])
        geometry.setAttribute( 'position', new BufferAttribute( vertices, 3 ) );
        const newArr = geometryByMaterialMap.get(colId)
        if (typeof(newArr) === 'undefined') {
          geometryByMaterialMap.set(colId, [geometry])
        } else {
          newArr.push(geometry)
          geometryByMaterialMap.set(colId, newArr)
        }
    }
    return geometryByMaterialMap
}
 
const View = () => {
  const { modelId } = useParams<ModelViewPageProps>();
  if (modelId === undefined || modelId === null) {
    throw new AssertionError(
        {message: `Expected modelId to be defined, but received ${modelId}`}
    )
  }
  const [bufGeos, setBufGeos] = useState<BufferGeometry[]>([])
  const [colors, setColors] = useState<number[][]>([])
  const [guids, setGuids] = useState<string[]>([])
  const [roots, setRoots] = useState<TreeNode[]>([])
  useEffect(() => {
    const allGeo = getAllModelGeometry(modelId)
    const bufGeos: BufferGeometry[] = []
    const colors: number[][] = []
    const guids: string[] = []
    /*
    for (const geo of allGeo) {
      if (geo.faceColors.length === 0) {
        // skip IfcSpace
        continue
      }
      const m = createGeometryByMaterialMap(geo)
      for (const [c, g] of m.entries()) {
        const merged = mergeBufferGeometries(g, false)
        merged.computeVertexNormals()
        bufGeos.push(merged)
        //setBufGeos([...bufGeos, merged])
        const rgba = c.split('-')
        colors.push([parseFloat(rgba[0]), parseFloat(rgba[1]), parseFloat(rgba[2]), parseFloat(rgba[3])])
        guids.push(geo.guid)
        //setColors([...colors, [parseFloat(rgba[0]), parseFloat(rgba[1]), parseFloat(rgba[2]), parseFloat(rgba[3])]])
        //setGuids([...guids, geo.guid])
      }
    }
    */
    setBufGeos(bufGeos)
    setColors(colors)
    setGuids(guids)
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
                  <GlbModels modelId={modelId}/>
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