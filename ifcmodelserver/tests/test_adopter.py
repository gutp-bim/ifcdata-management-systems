from unittest import TestCase
from pathlib import Path
from adopter import IFCOpenshellIFCModelAdopter
from model import IFCModelAdopter


class IFCOpenshellIFCModelAdopterTest(TestCase):

    def test_generate_ifcmodel(self):
        adopter = IFCOpenshellIFCModelAdopter()
        model = adopter.generate_ifcmodel("test_model", "test_data", "tests/resources/IfcOpenHouse_IFC4.ifc")

        assert len(model.instances) == 2885


if __name__ == '__main__':
    unittest.main()