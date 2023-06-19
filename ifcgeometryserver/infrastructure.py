from ifcopenshell.geom.main import settings
import ifcopenshell
from ifcopenshell import geom
import psycopg2
from typing import List
import itertools
from domain import (
    IfcFileAdopter, IfcFile, IfcGeometryDataDAO, IfcGeometryDataRepository,
    IfcGeometryData, IfcModelId, GloballyUniqueId, ClassName,
    Vertex, Normal, create_ifc_geometry_data, IfcGeometryData, Vertex, Normal)


from dto import IfcGeometryDataDTO, export_glb


class IfcOpenShellIfcFileAdopter(IfcFileAdopter):
    """"""

    def read_ifc_file(self, ifc_file: IfcFile) -> dict:
        settings = geom.settings()
        ifc_file = ifcopenshell.open(ifc_file.filepath.value)
        settings.set(settings.USE_WORLD_COORDS, True)
        settings.set(settings.WELD_VERTICES, False)
        settings.set(settings.NO_NORMALS, False)

        result = []
        products = ifc_file.by_type("IfcProduct")

        for product in products:
            if product.is_a("IfcOpeningElement"): continue
            if product.Representation:
                try:
                    shape = geom.create_shape(settings, product)
                    vertices: List[float] = [v for v in shape.geometry.verts]
                    indices: List[int] = [face for face in shape.geometry.faces]
                    normals: List[float] = [n for n in shape.geometry.normals]
                    face_colors = []
                    material_ids = shape.geometry.material_ids
                    materials = shape.geometry.materials

                    if len(materials) > 0 :
                        for material_id in material_ids:
                            material = materials[material_id]
                            if material_id == -1:
                                face_colors.append([0.0,0.0,0.0,0.0])
                            else:
                                material = materials[material_id]
                                diffuse = [1.0, 1.0, 1.0]
                                specular = [0, 0, 0]

                                if material.hasDiffuse():
                                    diffuse = list(material.diffuse)


                                face_colors.append(diffuse + [1.0 - material.transparency])

                    result.append({
                        "class_name": product.get_info()['type'],
                        "global_id": product.GlobalId,
                        "vertices": vertices,
                        "normals": normals,
                        "indices": indices,
                        "face_colors": face_colors
                    })
                except:
                    print("create shape error")
        return result


class PostgreSQLIfcGeometryDataRepository(IfcGeometryDataRepository):

    def __init__(self, host, port, database, user, password):
        """"""
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password


    def put(self, ifc_geometry_data_list: List[IfcGeometryData]):

        insert_query = """
            INSERT INTO ifcgeometry (ifcmodel_id, guid, classname, indices, vertices, normals, face_colors, geometry)
            VALUES (%s, %s, %s, %s, %s, %s, %s, ST_GeomFromEWKT(%s))
            """

        insert_elements = [(
            ifc_geometry_data.ifc_model_id.value,
            ifc_geometry_data.global_id.value,
            ifc_geometry_data.class_name.value,
            ifc_geometry_data.indices.value,
            self._convert_vertices(ifc_geometry_data.vertices),
            self._convert_vertices(ifc_geometry_data.normals),
            ifc_geometry_data.face_colors.value,
            self._generate_ewkt(ifc_geometry_data)) for ifc_geometry_data in ifc_geometry_data_list]

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(insert_query, insert_elements)
                conn.commit()

        self._put_glb(ifc_geometry_data_list[0].ifc_model_id.value, [ifc_geometry_data.to_dto() for ifc_geometry_data in ifc_geometry_data_list])
        return True


    def _put_glb(self, ifc_model_id: IfcModelId, geometries: List[IfcGeometryDataDTO]):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO ifcgeometryglb (ifcmodel_id, glb) VALUES (%s, %s)""", (ifc_model_id, export_glb(geometries)))
                conn.commit()

            
    def remove_by_ifcmodelid(self, a_ifcmodel_id: IfcModelId):

        delete_query = "DELETE FROM ifcgeometry WHERE ifcmodel_id = %s"

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(delete_query, (a_ifcmodel_id))
                conn.commit()
                return True


    def _convert_vertices(self, vertices: List[Vertex] ) -> List[float]:
        vertices_array = [[v.x, v.y, v.z] for v in vertices]
        return list(itertools.chain.from_iterable(vertices_array))


    def _convert_normals(self, normals: List[Normal] ) -> List[float]:
        normal_array = [[n.x, n.y, n.z] for n in normals]
        return list(itertools.chain.from_iterable(normal_array))


    def _convert_mesh_to_str(self, mesh:List[Vertex]) -> str:
        vertex_1 = mesh[0]
        vertex_2 = mesh[1]
        vertex_3 = mesh[2]

        vertex_1_str = '%s %s %s' % (str(vertex_1.x), str(vertex_1.y), str(vertex_1.z))
        vertex_2_str = '%s %s %s' % (str(vertex_2.x), str(vertex_2.y), str(vertex_2.z))
        vertex_3_str = '%s %s %s' % (str(vertex_3.x), str(vertex_3.y), str(vertex_3.z))
        return '((%s, %s, %s, %s))' % (vertex_1_str, vertex_2_str, vertex_3_str, vertex_1_str)


    def _generate_ewkt(self, ifc_geometry_data: IfcGeometryData) -> str:
        mesh_array = ifc_geometry_data.create_mesh()
        mesh_str_array = [ self._convert_mesh_to_str(mesh) for mesh in mesh_array]
        return 'POLYHEDRALSURFACE Z(' + ','.join(mesh_str_array) + ')'


    def _get_connection(self):
        """"""
        return psycopg2.connect(
            database=self._database,
            user = self._user,
            password = self._password,
            port=self._port,
            host=self._host
        )


class PostgreSQLIfcGeometryDataDAO(IfcGeometryDataDAO):

    def __init__(self, host, port, database, user, password):
        """"""
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password


    def find_by_ifcmodel_id(self, ifcmodel_id: str)-> List[IfcGeometryDataDTO]:
        """"""
        query = "SELECT ifcmodel_id, guid, classname, vertices, indices, normals, face_colors FROM ifcgeometry WHERE ifcmodel_id = %s"

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (ifcmodel_id,))
                conn.commit()
                result = cur.fetchall()
                return [IfcGeometryDataDTO(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in result]

    def find_by_global_id(self, ifcmodel_id: str, global_id:str) -> IfcGeometryDataDTO:
        """"""
        query = "SELECT ifcmodel_id, guid, classname, vertices, indices, normals, face_colors FROM ifcgeometry WHERE ifcmodel_id = %s AND guid=%s"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (ifcmodel_id, global_id, ))
                conn.commit()
                result = cur.fetchone()
                if result != None:
                    return IfcGeometryDataDTO(
                        result[0], result[1], result[2], result[3], result[4], result[5], result[6])
                else:
                    return None


    def find_by_class_name(self, ifcmodel_id: str, class_name: str) -> List[IfcGeometryDataDTO]:
        """"""
        query = "SELECT ifcmodel_id, guid, classname, vertices, indices, normals, face_colors FROM ifcgeometry WHERE ifcmodel_id = %s AND classname ILIKE %s"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (ifcmodel_id, class_name, ))
                conn.commit()
                result = cur.fetchall()
                return [IfcGeometryDataDTO(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in result]
   

                
    def find_glb_by_ifcmodel_id(self, ifcmodel_id: str) -> bytes:
        """"""
        query = "SELECT glb FROM ifcgeometryglb WHERE ifcmodel_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (ifcmodel_id, ))
                conn.commit()
                result = cur.fetchone()
                if result:
                    return bytes(result[0])
                else:
                    return None


    def _get_connection(self):
        """"""
        return psycopg2.connect(
            database=self._database,
            user = self._user,
            password = self._password,
            port=self._port,
            host=self._host
        )