from unittest import TestCase
from pathlib import Path
from adopter import IFCOpenshellIFCModelAdopter
from infrastructure import ArangoDBIFCModelRepository
from setup import database_setup


class ArangoDBIFCModelRepositoryTest(TestCase):

    def test_generate_ifcmodel(self):
        database_setup("tests/test_config.ini")
        adopter = IFCOpenshellIFCModelAdopter()
        model = adopter.generate_ifcmodel("test_model", "test_data", "tests/resources/IfcOpenHouse_IFC4.ifc")
        repository = ArangoDBIFCModelRepository("tests/test_config.ini")
        result = repository.put(model)
        assert result != None


if __name__ == '__main__':
    unittest.main()