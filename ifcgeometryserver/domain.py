import dataclasses
from abc import ABCMeta, abstractclassmethod
from typing import List
from dto import IfcGeometryDataDTO
import itertools


class Domain(metaclass=ABCMeta):
    """"""


class Value(metaclass=ABCMeta):
    """"""


@dataclasses.dataclass(frozen=True)
class FilePath(Value):
    """"""

    value: str

@dataclasses.dataclass(frozen=True)
class IfcFile(Domain):
    """"""

    filepath: FilePath


class IfcFileAdopter(metaclass=ABCMeta):
    """"""

    def read_ifc_file(ifc_file: IfcFile) -> dict:
        pass


@dataclasses.dataclass(frozen=True)
class IfcModelId(Value):
    """"""

    value: str


@dataclasses.dataclass(frozen=True)
class GloballyUniqueId(Value):
    """"""

    value: str


@dataclasses.dataclass(frozen=True)
class ClassName(Value):
    """"""

    value: str


@dataclasses.dataclass(frozen=True)
class Vertex(Value):
    """"""

    x: float
    y: float
    z: float


@dataclasses.dataclass(frozen=True)
class Indices(Value):
    """"""

    value: List[int]


@dataclasses.dataclass(frozen=True)
class Normal(Value):
    """"""

    x: float
    y: float
    z: float


@dataclasses.dataclass(frozen=True)
class FaceColors(Value):
    """"""

    value : List[List[float]]


@dataclasses.dataclass(frozen=True)
class IfcGeometryData(Domain):
    """"""

    ifc_model_id: IfcModelId
    global_id: GloballyUniqueId
    class_name: ClassName
    vertices: List[Vertex]
    normals: List[Normal]
    indices: Indices
    face_colors: FaceColors

    def create_mesh(self) -> list:
        indices_array = self.indices.value
        vertices = self.vertices
        return [[vertices[indices_array[i]], vertices[indices_array[i + 1]], vertices[indices_array[i + 2]]] for i in range(0, len(indices_array)-1, 3)]

    def to_json(self) -> dict:
        vertices = list(itertools.chain.from_iterable([[vertex.x, vertex.y, vertex.z] for vertex in self.vertices]))
        normals = list(itertools.chain.from_iterable([[normal.x, normal.y, normal.z] for normal in self.normals]))

        return {
            "ifc_model_id": self.ifc_model_id.value,
            "globally_unique_id": self.globally_unique_id.value,
            "class_name": self.class_name.value,
            "vertices": vertices,
            "normals": normals,
            "indices": self.indices.value,
            "face_color": self.face_color.value
        }

    def to_dto(self) -> IfcGeometryDataDTO:
        vertices = list(itertools.chain.from_iterable([[vertex.x, vertex.y, vertex.z] for vertex in self.vertices]))
        normals = list(itertools.chain.from_iterable([[normal.x, normal.y, normal.z] for normal in self.normals]))

        return IfcGeometryDataDTO(self.ifc_model_id.value, self.global_id.value, self.class_name.value, vertices, self.indices.value, normals, self.face_colors.value)


class IfcGeometryDataRepository(metaclass=ABCMeta):
    """"""

    @abstractclassmethod
    def put(self, ifc_geometry_data_list: List[IfcGeometryData]):
        pass


class IfcGeometryDataDAO(metaclass=ABCMeta):

    @abstractclassmethod
    def find_by_ifcmodel_id(self, ifc_model_id:IfcModelId)-> List[IfcGeometryDataDTO]:
        pass

    @abstractclassmethod
    def find_by_global_id(self, ifc_model_id: IfcModelId, globally_unique_id:GloballyUniqueId) -> IfcGeometryDataDTO:
        pass

    @abstractclassmethod
    def find_by_class_name(self, ifc_model_id: IfcModelId, class_name: ClassName) -> List[IfcGeometryDataDTO]:
        pass

    @abstractclassmethod
    def find_glb_by_ifcmodel_id(self, ifcmodel_id: str, lod: int) -> bytes:
        pass


def create_ifc_file(filepath:str) -> IfcFile:
    """"""
    return IfcFile(FilePath(filepath))


def create_ifc_geometry_data_from_file(ifc_model_id: str, filepath:str, adopter: IfcFileAdopter) -> List[IfcGeometryData]:
    """"""
    ifc_model_id_value = IfcModelId(ifc_model_id)
    file = create_ifc_file(filepath)
    geometry_dict = adopter.read_ifc_file(file)

    result = []
    for element in geometry_dict:
        global_id = GloballyUniqueId(element["global_id"])
        class_name =  ClassName(element["class_name"])
        vertices = element["vertices"]
        normals = element["normals"]
        indices = Indices(element["indices"])
        face_colors = FaceColors(element["face_colors"])
        vertex_array = [Vertex(vertices[i], vertices[i + 1], vertices[i + 2]) for i in range(0, len(vertices), 3)]
        normal_array = [Vertex(normals[i], normals[i + 1], normals[i + 2]) for i in range(0, len(normals), 3)]
        geometry_data = IfcGeometryData(
            ifc_model_id_value, global_id, class_name,
            vertex_array, normal_array, indices, face_colors)
        result.append(geometry_data)

    return result

def create_ifc_geometry_data(
    ifc_model_id: str, globally_unique_id:str, class_name:str,
    vertices:List[float], normals:List[float], indices:List[int], face_colors:List[List[float]]) -> IfcGeometryData:
    return IfcGeometryData(
        IfcModelId(ifc_model_id), GloballyUniqueId(globally_unique_id), ClassName(class_name),
        [Vertex(vertices[i], vertices[i + 1], vertices[i + 2]) for i in range(0, len(vertices), 3)],
        [Normal(normals[i], normals[i + 1], normals[i + 2]) for i in range(0, len(normals), 3)],
        Indices(indices), FaceColors(face_colors))