import React, { useState, useContext } from 'react';
import { AiOutlinePlusSquare, AiOutlineMinusSquare } from "react-icons/ai";

import { guidContext } from './contexts'
import { TreeNode } from 'innerDataModel/TreeNode';

import 'styles.css'

type TreeRowProps = {node: TreeNode; level: number}

const TreeRow = ({node, level}: TreeRowProps) => {
  const ctx = useContext(guidContext)
  const isFocused = node.guid === ctx.guid
  const handleClick = (e: React.MouseEvent<Element, MouseEvent>) => {
    e.stopPropagation()
    ctx.setNewGuid(node.guid)
  }

  const [expanded, setExpanded] = useState(false);
  const arrayForSpace = level===0? [...Array(0)] : [...Array(level+1).keys()];
 
  return (
    <>
      <div style={{backgroundColor: isFocused ? "yellow" : "white", height: "23px"}}>
        <div style={{ display: "inline-block", height: "23px", width: "3px"}} />
        {arrayForSpace.map((idx) => {
          if (idx == 0) {
            return <div style={{ display: "inline-block", height: "22px", width: "7px" }} />
          } else if (idx == level) {
            return <div style={{ display: "inline-block", height: "22px", width: "8px", borderLeft: "2px dashed #A9A9A9"}} />
          } else {
            return <div style={{ display: "inline-block", height: "22px", width: "15px", borderLeft: "2px dashed #A9A9A9"}} />
          }    
        })}
        {node.children?.length ? (
          expanded
            ? <AiOutlineMinusSquare onClick={() => setExpanded((current) => !current)} style={{ display: "inline-block", verticalAlign: "8%" }}/>
            : <AiOutlinePlusSquare onClick={() => setExpanded((current) => !current)} style={{ display: "inline-block", verticalAlign: "8%" }} />
        ) : <div style={{ display: "inline-block", paddingLeft: "16px"}} />}
        <div
          style={{ display: "inline-block", cursor: "pointer", userSelect: "none", paddingLeft: "3px", verticalAlign: "top" }}
          onDoubleClick={(e) => handleClick(e)}
        >{node.type}</div>
        <div
          style={{ display: "inline-block", cursor: "pointer", userSelect: "none", paddingLeft: "3px", verticalAlign: "30%", fontSize: "small", color: "#A9A9A9" }}
          onDoubleClick={(e) => handleClick(e)}
        >{node.guid}</div>
      </div>
      {
        expanded &&
        node.children?.map((childNode) => {
          return (
            <TreeRow
              key={`${childNode.type}-${childNode.guid}`}
              node={childNode}
              level={level+1}
            />
          )
          }
        )
      }
    </>
  )
}

export default TreeRow