import trimesh
from domain import IfcGeometryData
from typing import List


def convert_ifcgeometrydata_list(geometries:List[IfcGeometryData]):

    scene = trimesh.Scene()

    for geometry in geometries:

        metadata = {
            "GloballyUniqueId": geometry.globally_unique_id.value,
            "ClassName": geometry.class_name.value
                    }

        vertices = geometry.vertices
        indices = geometry.indices.value

        trimesh_vertices = [[v.x, v.y, v.z] for v in vertices]
        trimesh_indices = [[indices[i], indices[i+1], indices[i+2]] for i in range(0, len(indices), 3)]

        mesh = trimesh.Trimesh(
            vertices=trimesh_vertices, faces=trimesh_indices,
            metadata=metadata, geometry=geometry.face_color.value)

        scene.add_geometry(mesh)

    return trimesh.exchange.gltf.export_gltf(scene)