import dataclasses
from typing import List

@dataclasses.dataclass(frozen=True)
class IfcGeometryDataDTO(object):

    ifcmodel_id: str
    global_id: str
    class_name: str
    vertices: List[float]
    indices: List[int]
    normals: List[float]
    face_colors: List[List[float]]

    def to_json(self):
        return {
            "ifcmodel_id": self.ifcmodel_id,
            "globally_unique_id": self.global_id,
            "class_name": self.class_name,
            "vertices": self.vertices,
            "indices": self.indices,
            "normals": self.normals,
            "face_colors": self.face_colors
        }


def export_glb(geometries: List[IfcGeometryDataDTO], boxel_sizes=[0, 0.01, 0.05]):
    # boxel_size=0 means no simplification.
    import trimesh

    scenes = {boxel_size: trimesh.Scene() for boxel_size in boxel_sizes}

    for geometry in geometries:
        vertices = geometry.vertices
        indices = geometry.indices
        face_colors = geometry.face_colors

        vertex_list = [[vertices[i], vertices[i+1], vertices[i+2]] for i in range(0, len(vertices), 3)]
        faces = [[indices[i], indices[i+1], indices[i+2]] for i in range(0, len(indices), 3)]

        if len(face_colors) > 0:
            default_mesh = trimesh.Trimesh(vertices = vertex_list, faces=faces, face_colors=geometry.face_colors)
        else:
            default_mesh = trimesh.Trimesh(vertices = vertex_list, faces=faces)
        for boxel_size in scenes.keys():
            cur_scene = scenes[boxel_size]
            if boxel_size == 0:
                default_mesh.metadata = {
                                "ifcmodel_id": geometry.ifcmodel_id,
                                "global_id": geometry.global_id,
                                "class_name": geometry.class_name
                            }
                cur_scene.add_geometry(default_mesh)
            else:
                simple = to_open3d(default_mesh).simplify_vertex_clustering(boxel_size)
                simple_trimesh = trimesh.Trimesh(
                            vertices = simple.vertices, faces=simple.triangles, vertex_colors=simple.vertex_colors,
                            metadata= {
                                "ifcmodel_id": geometry.ifcmodel_id,
                                "global_id": geometry.global_id,
                                "class_name": geometry.class_name
                            })
                cur_scene.add_geometry(simple_trimesh)
            scenes[boxel_size] = cur_scene
    return [scene.export(None, "glb") for scene in scenes.values()]

def to_open3d(mesh):
    import open3d
    import numpy as np
    o3d_mesh = open3d.geometry.TriangleMesh()
    o3d_mesh.vertices = open3d.utility.Vector3dVector(np.array(mesh.vertices.copy()))
    o3d_mesh.triangles = open3d.utility.Vector3iVector(np.array(mesh.faces.copy()))
    o3d_mesh.vertex_colors = open3d.utility.Vector3dVector(np.array([[rgba[0]/255, rgba[1]/255, rgba[2]/255] for rgba in mesh.visual.vertex_colors]))
    return o3d_mesh