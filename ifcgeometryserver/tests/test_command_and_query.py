import configparser
from domain import GloballyUniqueId
import unittest
import psycopg2
from infrastructure import PostgreSQLIfcGeometryDataRepository, IfcOpenShellIfcFileAdopter
from command import CommandHandler, StoreIFCGeometryData
from query import  QueryHandler, GetGeometryDataByIFCModelId, GetGeometryDataByGloballyUniqueId, GetGeometryDataByClassName


class TestCommandAndQuery(unittest.TestCase):
    """"""

    def setUp(self) -> None:
        config = configparser.ConfigParser()
        config.read("./tests/testconfig.ini", encoding="utf-8")
        self._host = config["database"]["host"]
        self._port = int(config["database"]["port"])
        self._database = config["database"]["database_name"]
        self._user = config["database"]["user"]
        self._password = config["database"]["password"]


    def test_upload_and_find(self):
        """"""
        repository = PostgreSQLIfcGeometryDataRepository(
            host=self._host, port=self._port, database=self._database, user=self._user, password=self._password)
        adopter = IfcOpenShellIfcFileAdopter()
        command_handler = CommandHandler(adopter, repository)
        query_handler = QueryHandler(repository)
        command = StoreIFCGeometryData("test12345", "/app/tests/resources/testmodel.ifc")
        command_handler.handle(command)
        query = GetGeometryDataByIFCModelId("test12345")
        result = query_handler.handle(query)
        self.assertNotEqual(len(result), 0)
        query2 = GetGeometryDataByGloballyUniqueId("test12345", "2$s0cM5$P6GvYXYiPxs6$1")
        result2 = query_handler.handle(query2)
        self.assertEqual(result2.globally_unique_id, GloballyUniqueId("2$s0cM5$P6GvYXYiPxs6$1"))
        query3 = GetGeometryDataByClassName("test12345", "IfcSpace")
        result3 = query_handler.handle(query3)
        self.assertNotEqual(len(result3), 0)


    def tearDown(self):
        with psycopg2.connect(
            host=self._host, port=self._port, database=self._database,
            user=self._user, password=self._password) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ifcgeometry")


if __name__ == "__main__":
    unittest.main()