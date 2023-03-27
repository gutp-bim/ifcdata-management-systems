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


def export_glb(geometries: List[IfcGeometryDataDTO]):
    import trimesh

    scene = trimesh.Scene()

    for geometry in geometries:
        vertices = geometry.vertices
        indices = geometry.indices
        face_colors = geometry.face_colors

        vertex_list = [[vertices[i], vertices[i+1], vertices[i+2]] for i in range(0, len(vertices), 3)]
        faces = [[indices[i], indices[i+1], indices[i+2]] for i in range(0, len(indices), 3)]

        if len(face_colors) > 0:
            mesh = trimesh.Trimesh(
                vertices = vertex_list, faces=faces, face_colors=geometry.face_colors,
                metadata= {
                    "ifcmodel_id": geometry.ifcmodel_id,
                    "global_id": geometry.global_id,
                    "class_name": geometry.class_name
                })
            scene.add_geometry(mesh)
        else:
            mesh = trimesh.Trimesh(
                vertices = vertex_list, faces=faces,
                metadata= {
                    "ifcmodel_id": geometry.ifcmodel_id,
                    "global_id": geometry.global_id,
                    "class_name": geometry.class_name
                })
            scene.add_geometry(mesh)

    return scene.export(None, "glb")