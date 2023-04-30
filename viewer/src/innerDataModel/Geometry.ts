export type Geometry = {
    guid: string;
    faceColors: number[][];
    vertices: number[];
    indices: number[]; 
};

export const Geometry = {
    make: (guid: string, faceColors: number[][], vertices: number[], indices: number[]):  Geometry => {
        return {
            guid: guid,
            faceColors: faceColors,
            vertices: vertices,
            indices: indices
        }
    }
}