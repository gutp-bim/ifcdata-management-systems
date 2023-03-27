from unittest import TestCase
import inject
from rdflib import RDFS, RDF
from rdflib.namespace import Namespace
from model import IFCModelRepository, IFCInstanceDAO, IFCModelDAO
from command import IFCModelCommandHandler, UploadIFCModelByStepFile
from query import IFCModelQueryHandler, FindIFCInstancesForBOT
from dto import ifcinstances_to_lbd
from infrastructure import ArangoDBIFCModelRepository, ArangoDBIFCModelDAO, ArangoDBIFCInstanceDAO
from setup import database_setup



def config(binder):
    binder.bind(IFCModelRepository, ArangoDBIFCModelRepository("tests/test_config.ini"))
    binder.bind(IFCInstanceDAO, ArangoDBIFCInstanceDAO("tests/test_config.ini"))
    binder.bind(IFCModelDAO, ArangoDBIFCModelDAO("tests/test_config.ini"))


class LBDWriteTest(TestCase):

    def setUp(self):
        database_setup("tests/test_config.ini")
        inject.configure(config)
        self._command_handler = IFCModelCommandHandler()
        self._query_handler = IFCModelQueryHandler()


    def test_write_simplebot_1(self):
        BOT = Namespace("https://w3id.org/bot#")
        upload_command = UploadIFCModelByStepFile(
            "tests/resources/testmodel.ifc", "lbdtest", "lbdtest")
        upload_result = self._command_handler.handle(upload_command)
        query = FindIFCInstancesForBOT(upload_result.value)
        instances = self._query_handler.handle(query)
        bot_result = ifcinstances_to_lbd("http://test.org/", instances)

        site_count = len(list(bot_result.triples((None, RDF.type, BOT.Site))))
        building_count = len(list(bot_result.triples((None, RDF.type, BOT.Building))))
        storey_count = len(list(bot_result.triples((None, RDF.type, BOT.Storey))))
        space_count = len(list(bot_result.triples((None, RDF.type, BOT.Space))))
        print(space_count)

        assert site_count == 1
        assert building_count == 1
        assert storey_count == 1
        assert space_count == 10