import React, {useState, useEffect} from 'react';
import data from '../bot.json';
import { TreeNode } from 'innerDataModel/TreeNode';

type BotData = {
    "@id": string;
    "@type": string[];
    "http://www.buildingsmart-tech.org/IFC4#GlobalId": {"@value": string}[];
    "http://www.buildingsmart-tech.org/IFC4#LongName"?: object[];
    "http://www.buildingsmart-tech.org/IFC4#Name"?: object[];
    "http://www.buildingsmart-tech.org/IFC4#RefElevation"?: object[];
    "http://www.buildingsmart-tech.org/IFC4#RefLatitude"?: object[];
    "http://www.buildingsmart-tech.org/IFC4#RefLongitude"?: object[];
    "https://w3id.org/bot#hasBuilding"?: {"@id": string}[];
    "https://w3id.org/bot#hasStorey"?: {"@id": string}[];
    "https://w3id.org/bot#hasSpace"?: {"@id": string}[];
    "https://w3id.org/bot#hasElement"?: {"@id": string}[];
}

export const useGetTreeData: ((modelId: string) => TreeNode[]) = (modelId: string) => {
    const [posts, setPosts] = useState<TreeNode[]>([])
    useEffect(() => {
        fetch(`http://localhost:8080/v1/bot/${modelId}.jsonld`, {method: 'GET'})
        .then(res => res.json())
        .then(data => {
            console.log('get data')
            isBotData(data) && setPosts(fromBotToInnerModel(data))
        })
    }, [])

    return posts
}

const isBotData = (data: any): data is BotData[] => {
    return true
}

const fromBotToInnerModel: ((data: BotData[]) => TreeNode[]) = (data: BotData[]) => {
    console.log('exchanger called')
    const all = data
    // Not assign any type here because bot data type does not match any data type.
    const queue: {bot: BotData, node: TreeNode}[] = []
    // find Site element
    const site = all.find(el => el["@type"][0] === "https://w3id.org/bot#Site")
    if (typeof site === 'undefined') {
     return []
    }
    const root: TreeNode = {
     guid: site["http://www.buildingsmart-tech.org/IFC4#GlobalId"][0]["@value"],
     type: "Site",
     children: []
    }
    queue.push({bot: site, node: root})
    while (queue.length > 0) {
     const el = queue.shift()
     if (typeof el === 'undefined') {
         continue
     }
     const botData = el.bot
     const nodeData = el.node
     switch (el.node.type) {
         case "Site":
             for (const child of el.bot["https://w3id.org/bot#hasBuilding"] || []) {
                 const bot = all.find(el => el["@id"] === child["@id"])
                 if (typeof bot === 'undefined') {
                     continue
                 }
                 const node: TreeNode = {
                     guid: bot["http://www.buildingsmart-tech.org/IFC4#GlobalId"][0]["@value"],
                     type: "Building",
                     children: []
                 }
                 el.node.children.push(node)
                 queue.push({bot: bot, node: node})
             }
             break;
         case "Building":
             for (const child of el.bot["https://w3id.org/bot#hasStorey"] || []) {
                 const bot = all.find(el => el["@id"] === child["@id"])
                 if (typeof bot === 'undefined') {
                     continue
                 }
                 const node: TreeNode = {
                     guid: bot["http://www.buildingsmart-tech.org/IFC4#GlobalId"][0]["@value"],
                     type: "Storey",
                     children: []
                 }
                 el.node.children.push(node)
                 queue.push({bot: bot, node: node})
             }
             break;
         case "Storey":
             for (const child of el.bot["https://w3id.org/bot#hasSpace"] || []) {
                 const bot = all.find(el => el["@id"] === child["@id"])
                 if (typeof bot === 'undefined') {
                     continue
                 }
                 const node: TreeNode = {
                     guid: bot["http://www.buildingsmart-tech.org/IFC4#GlobalId"][0]["@value"],
                     type: "Space",
                     children: []
                 }
                 el.node.children.push(node)
                 queue.push({bot: bot, node: node})
             }
             for (const child of el.bot["https://w3id.org/bot#hasElement"] || []) {
                 const bot = all.find(el => el["@id"] === child["@id"])
                 if (typeof bot === 'undefined') {
                     continue
                 }
                 const node: TreeNode = {
                     guid: bot["http://www.buildingsmart-tech.org/IFC4#GlobalId"][0]["@value"],
                     type: "Element",
                     children: []
                 }
                 el.node.children.push(node)
             }
             break;
         case "Space":
             for (const child of el.bot["https://w3id.org/bot#hasSpace"] || []) {
                 const bot = all.find(el => el["@id"] === child["@id"])
                 if (typeof bot === 'undefined') {
                     continue
                 }
                 const node: TreeNode = {
                     guid: bot["http://www.buildingsmart-tech.org/IFC4#GlobalId"][0]["@value"],
                     type: "Space",
                     children: []
                 }
                 el.node.children.push(node)
             }
             for (const child of el.bot["https://w3id.org/bot#hasElement"] || []) {
                 const bot = all.find(el => el["@id"] === child["@id"])
                 if (typeof bot === 'undefined') {
                     continue
                 }
                 const node: TreeNode = {
                     guid: bot["http://www.buildingsmart-tech.org/IFC4#GlobalId"][0]["@value"],
                     type: "Element",
                     children: []
                 }
                 el.node.children.push(node)
             }
             break;
         case "Element":
             break;
     }
    }
    return [root]
}