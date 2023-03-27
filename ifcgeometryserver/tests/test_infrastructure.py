import unittest
import configparser
from domain import IfcFile, IfcModelId, GloballyUniqueId, ClassName, create_ifc_file, create_ifc_geometry_data_from_file
from infrastructure import IfcOpenShellIfcFileAdopter, PostgreSQLIfcGeometryDataRepository, PostgreSQLIfcGeometryDataDAO
import psycopg2


class TestIfcOpenShellIfcFileAdopter(unittest.TestCase):
    """test class of ifcenginewrapper.py
    """

    def test_read_ifc_file(self):
        """
            test read_ifc_file method
        """

        test_file = create_ifc_file('./tests/resources/testmodel.ifc')
        ifc_file_adopter = IfcOpenShellIfcFileAdopter()
        result = ifc_file_adopter.read_ifc_file(test_file)
        self.assertNotEqual(len(result), 0)


class TestPostgreSQLIfcGeometryDataRepository(unittest.TestCase):
    """"""

    def setUp(self):
        config = configparser.ConfigParser()
        config.read("./tests/testconfig.ini", encoding="utf-8")
        self._host = config["database"]["host"]
        self._port = int(config["database"]["port"])
        self._database = config["database"]["database_name"]
        self._user = config["database"]["user"]
        self._password = config["database"]["password"]

    def test_put(self):
        """"""
        adopter = IfcOpenShellIfcFileAdopter()
        repository = PostgreSQLIfcGeometryDataRepository(
            host=self._host, port=self._port, database=self._database, user=self._user, password=self._password)
        geometries = create_ifc_geometry_data_from_file('testid12345', './tests/resources/testmodel.ifc', adopter)
        assert repository.put(geometries)

    def tearDown(self):
        with psycopg2.connect(
            host=self._host, port=self._port, database=self._database, user=self._user, password=self._password) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ifcgeometry")


class TestPostgreSQLIfcGeometryDataDAO(unittest.TestCase):

    def setUp(self):
        config = configparser.ConfigParser()
        config.read("./tests/testconfig.ini", encoding="utf-8")
        self._host = config["database"]["host"]
        self._port = int(config["database"]["port"])
        self._database = config["database"]["database_name"]
        self._user = config["database"]["user"]
        self._password = config["database"]["password"]


    def test_find_geometries(self):
        adopter = IfcOpenShellIfcFileAdopter()
        repository = PostgreSQLIfcGeometryDataRepository(
            host=self._host, port=self._port, database=self._database, user=self._user, password=self._password
        )
        dao = PostgreSQLIfcGeometryDataDAO(
            host=self._host, port=self._port, database=self._database, user=self._user, password=self._password
        )
        geometries = create_ifc_geometry_data_from_file('testid12345', './tests/resources/testmodel.ifc', adopter)
        repository.put(geometries)

        result = dao.find_by_ifcmodel_id("testid12345")
        self.assertNotEqual(len(result), 0)
        result2 = dao.find_by_global_id("testid12345", '2$s0cM5$P6GvYXYiPxs6$1')
        self.assertEqual(result2.global_id, '2$s0cM5$P6GvYXYiPxs6$1')
        result3 = dao.find_by_class_name("testid12345", "IfcSpace")
        self.assertNotEqual(len(result3), 0)

    def tearDown(self):
        with psycopg2.connect(
            host=self._host, port=self._port, database=self._database, user=self._user, password=self._password) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ifcgeometry")

if __name__ == "__main__":
    unittest.main()