type Type = "Site" | "Building" | "Storey" | "Space" | "Element"

export type TreeNode = {
    guid: string;
    type: Type;
    children: TreeNode[]
}