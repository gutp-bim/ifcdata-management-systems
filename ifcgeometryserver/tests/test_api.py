from falcon import testing
import configparser
import api
from requests_toolbelt import MultipartEncoder
import psycopg2



class APITestCase(testing.TestCase):
    def setUp(self):
        super(APITestCase, self).setUp()
        self.app = api.create_app()
        config = configparser.ConfigParser()
        config.read("./tests/testconfig.ini", encoding="utf-8")
        self._host = config["database"]["host"]
        self._port = int(config["database"]["port"])
        self._database = config["database"]["database_name"]
        self._user = config["database"]["user"]
        self._password = config["database"]["password"]


class TestAPI(APITestCase):

    def test_upload_ifc_file(self):

        with open("./tests/resources/testmodel.ifc", "rb") as ifcfile:
            post_data = MultipartEncoder({
                "ifcmodel_id": "test12345",
                "upfile": ("testmodel.ifc", ifcfile, "text/plain")
            })
            result = self.simulate_post(
                "/v1/ifcgeometry/upload",
                body=post_data.read() ,
                headers={"content-type":post_data.content_type})
            self.assertEqual(result.json["message"], "upload finished")

            result2 = self.simulate_get("/v1/ifcgeometry/test12345")
            self.assertNotEqual(len(result2.json["geometries"]), 0)

            result3 = self.simulate_get(path="/v1/ifcgeometry/test12345", query_string="class=IfcWallStandardCase")
            self.assertEqual(len(result3.json["geometries"]), 4)

            result4 = self.simulate_get("/v1/ifcgeometry/test12345/2EDq6SkG19ohsF7ZtIUJww")
            self.assertEqual(result4.json["geometry"]["class_name"], "IfcWallStandardCase")

    def tearDown(self):
        with psycopg2.connect(
            host=self._host, port=self._port, database=self._database, user=self._user, password=self._password) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ifcgeometry")