import { GLTF } from 'three/examples/jsm/loaders/GLTFLoader';

export type GLTFResult = GLTF & {
    nodes: Object
    materials: {
        '': THREE.MeshStandardMaterial
    }
}