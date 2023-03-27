from unittest import TestCase
from pathlib import Path
from adopter import IFCOpenshellIFCModelAdopter
from infrastructure import ArangoDBIFCModelRepository, ArangoDBIFCModelDAO, ArangoDBIFCInstanceDAO
from setup import database_setup


class ArangoDBIFCModelDAOAndArangoDBIFCInstanceDAOTest(TestCase):

    def test_generate_ifcmodel(self):
        config_path = "tests/test_config.ini"
        database_setup(config_path)
        adopter = IFCOpenshellIFCModelAdopter()
        model = adopter.generate_ifcmodel("test_model", "test_data", "tests/resources/IfcOpenHouse_IFC4.ifc")
        repository = ArangoDBIFCModelRepository(config_path)
        model_dao = ArangoDBIFCModelDAO(config_path)
        instance_dao = ArangoDBIFCInstanceDAO(config_path)
        result = repository.put(model)

        models = model_dao.find_all()
        instances = instance_dao.find_all(result.value)
        model = model_dao.find_by_ifcmodelid(result.value)
        instance = instance_dao.find_by_ifcinstanceid(instances[0].ifcinstance_id)
        stories = instance_dao.find_by_classname(result.value, "IfcBuildingStorey")

        instances_for_lbd = instance_dao.find_for_bot(result.value)
        for instance in instances_for_lbd:
            print(instance)
        
        assert len(models) > 0
        assert len(instances) == 2885
        assert model != None
        assert instance != None
        assert len(stories) > 0
        assert len(instances_for_lbd)

if __name__ == '__main__':
    unittest.main()