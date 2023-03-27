from model import *
from arango import ArangoClient
import configparser
import itertools


class ArangoDBIFCModelRepository(IFCModelRepository):

    def __init__(self, file_path):
        config = configparser.ConfigParser()
        config.read(file_path)
        self._hosts = config['DATABASE']['hosts']
        self._user = config['DATABASE']['user']
        self._password = config['DATABASE']['password']
        self._db_name = config['DATABASE']['db_name']
        self._graph = config['DATABASE']['graph']
        self._ifc_model = config['DATABASE']['ifc_model']
        self._ifc_instance = config['DATABASE']['ifc_instance']
        self._belongs = config['DATABASE']['belongs']
        self._reference = config['DATABASE']['reference']
        self._inverse = config['DATABASE']['inverse']

    def put(self, a_ifcmodel: IFCModel):

        print("start upload")

        model_dict = {
            "_key": a_ifcmodel.ifcmodel_id.value,
            "model_name": a_ifcmodel.model_name.value,
            "description": a_ifcmodel.description.value,
            "schema_version": a_ifcmodel.schema_version.value}

        instances = a_ifcmodel.instances

        instance_dict_list = [{
            "_key": instance.instance_id.value,
            "class_name": instance.classname.value,
            "attributes": [ attribute.to_dict() for attribute in instance.attributes]
            } for instance in instances]

        print("data convert")

        model_result = None

        try:
            client = ArangoClient(hosts=self._hosts)
            db = client.db(self._db_name, username=self._user, password=self._password)
            graph = db.graph(self._graph)
            ifcmodel_collection = graph.vertex_collection(self._ifc_model)
            model_result = ifcmodel_collection.insert(model_dict)

            print("create model")

            ifcinstance_collection = graph.vertex_collection(self._ifc_instance)
            instance_result = ifcinstance_collection.import_bulk(instance_dict_list)

            print("create instance")
        finally:
            client.close()

        belongs_list = [{
            "_from": self._ifc_model + "/" + a_ifcmodel.ifcmodel_id.value,
            "_to": self._ifc_instance + "/" + instance.instance_id.value
            } for instance in instances]

        def create_reference_dict(e: IFCInstance):
            references = e.get_references()
            return [{
                "_from": self._ifc_instance + "/" + e.instance_id.value,
                "_to": self._ifc_instance + "/" + reference[1].value.value,
                "attribute_name": reference[0].value
            } for reference in references]

        def create_inverse_dict(e: IFCInstance):
            inverses= e.inverses
            nest_dict_list = [[{
                "_from": self._ifc_instance + "/" + v.value,
                "_to": self._ifc_instance + "/" + e.instance_id.value,
                "inverse_name": inverse.inverse_name.value
                }   for v in inverse.value]for inverse in inverses]
            return list(itertools.chain.from_iterable(nest_dict_list))
        nest_inverse_dict_list = [ create_inverse_dict(instance) for instance in instances]
        inverse_dict_list = list(itertools.chain.from_iterable(nest_inverse_dict_list))
        nest_reference_dict_list = [ create_reference_dict(instance) for instance in instances]
        reference_dict_list = list(itertools.chain.from_iterable(nest_reference_dict_list))

        client = ArangoClient(hosts=self._hosts)
        db = client.db(self._db_name, username=self._user, password=self._password)
        async_db = db.begin_async_execution(return_result=True)
        graph = async_db.graph(self._graph)
        belongs_collection = graph.edge_collection(self._belongs)
        reference_collection = graph.edge_collection(self._reference)
        inverse_collection = graph.edge_collection(self._inverse)

        belongs_collection.import_bulk(belongs_list)
        reference_collection.import_bulk(reference_dict_list)
        inverse_collection.import_bulk(inverse_dict_list)


        return IFCModelId(model_result["_key"])


    def remove_by_ifcmodelid(self, a_ifcmodel_id: IFCModelId):
        pass



from dto import *

class ArangoDBIFCModelDAO(IFCModelDAO):

    def __init__(self, file_path):
        config = configparser.ConfigParser()
        config.read(file_path)
        self._hosts = config['DATABASE']['hosts']
        self._user = config['DATABASE']['user']
        self._password = config['DATABASE']['password']
        self._db_name = config['DATABASE']['db_name']
        self._graph = config['DATABASE']['graph']
        self._ifc_model = config['DATABASE']['ifc_model']
        self._ifc_instance = config['DATABASE']['ifc_instance']
        self._belongs = config['DATABASE']['belongs']
        self._reference = config['DATABASE']['reference']
        self._inverse = config['DATABASE']['inverse']

    def find_all(self):
        client = ArangoClient(hosts=self._hosts)
        db = client.db(self._db_name, username=self._user, password=self._password)
        graph = db.graph(self._graph)
        ifcmodel_collection = graph.vertex_collection(self._ifc_model)
        client.close()
        return [IFCModelDTO(
                ifcmodel["_key"], ifcmodel["schema_version"], ifcmodel["model_name"], ifcmodel["description"]
            ) for ifcmodel in ifcmodel_collection]

    def find_by_ifcmodelid(self, ifcmodel_id):
        client = ArangoClient(hosts=self._hosts)
        db = client.db(self._db_name, username=self._user, password=self._password)
        graph = db.graph(self._graph)
        ifcmodel_collection = graph.vertex_collection(self._ifc_model)
        result = ifcmodel_collection.find({"_key": ifcmodel_id})
        client.close()
        if len(result) == 1:
            ifcmodel = result.next()
            return IFCModelDTO(
                ifcmodel["_key"], ifcmodel["schema_version"], ifcmodel["model_name"], ifcmodel["description"])
        else:
            return None


class ArangoDBIFCInstanceDAO(IFCInstanceDAO):

    def __init__(self, file_path):
        config = configparser.ConfigParser()
        config.read(file_path)
        self._hosts = config['DATABASE']['hosts']
        self._user = config['DATABASE']['user']
        self._password = config['DATABASE']['password']
        self._db_name = config['DATABASE']['db_name']
        self._graph = config['DATABASE']['graph']
        self._ifc_model = config['DATABASE']['ifc_model']
        self._ifc_instance = config['DATABASE']['ifc_instance']
        self._belongs = config['DATABASE']['belongs']
        self._reference = config['DATABASE']['reference']
        self._inverse = config['DATABASE']['inverse']

    def find_all(self, ifcmodel_id):
        client = ArangoClient(hosts=self._hosts)
        db = client.db(self._db_name, username=self._user, password=self._password)
        aql = db.aql
        cursor = db.aql.execute(
            """FOR instance IN 1..1 OUTBOUND @ifcmodelid belongs RETURN instance""",
            bind_vars={"ifcmodelid": self._ifc_model + "/" + ifcmodel_id}
        )
        client.close()
        return [self._convert_result(result) for result in cursor]

    def find_by_ifcinstanceid(self, ifcinstanceid):
        client = ArangoClient(hosts=self._hosts)
        db = client.db(self._db_name, username=self._user, password=self._password)
        graph = db.graph(self._graph)
        ifcinstance_collection = graph.vertex_collection(self._ifc_instance)
        result = ifcinstance_collection.find({"_key": ifcinstanceid})
        if len(result) == 1:
            return self._convert_result(result.next())
        else:
            return None

    def find_by_classname(self, ifcmodel_id, class_name):
        client = ArangoClient(hosts=self._hosts)
        db = client.db(self._db_name, username=self._user, password=self._password)
        aql = db.aql
        cursor = db.aql.execute(
            """FOR instance IN 1..1 OUTBOUND @ifcmodelid belongs FILTER instance.class_name == @class_name RETURN instance""",
            bind_vars={"ifcmodelid": self._ifc_model + "/" + ifcmodel_id, "class_name": class_name}
        )
        client.close()
        return [self._convert_result(result) for result in cursor]


    def find_by_guid(self, ifcmodel_id, guid):
        client = ArangoClient(hosts=self._hosts)
        db = client.db(self._db_name, username=self._user, password=self._password)
        aql = db.aql
        query = """
        FOR instance IN 1..1 OUTBOUND @ifcmodelid belongs
            LET guid_attribute = (FOR attribute IN instance.attributes
            FILTER attribute.attribute_name == "GlobalId"
                && attribute.attribute_value.value == @guid
            RETURN attribute)
            FILTER guid_attribute != []
        RETURN instance
        """
        cursor = db.aql.execute(
            query,
            bind_vars={"ifcmodelid": self._ifc_model + "/" + ifcmodel_id, "guid": guid}
        )
        client.close()
        return [self._convert_result(result) for result in cursor][0]


    def find_by_inverse_name(self, ifcinstance_id, inverse_name):
        client = ArangoClient(hosts=self._hosts)
        db = client.db(self._db_name, username=self._user, password=self._password)
        aql = db.aql

        query = """
            FOR instance in ifc_instance
            FILTER instance._id == @ifcinstance_id
            FOR result, i IN 1..1 INBOUND instance inverse
            FILTER i.inverse_name == @inverse_name
            RETURN result
        """
        cursor = db.aql.execute(
            query,
            bind_vars={"ifcinstance_id": self._ifc_instance + "/" + ifcinstance_id, "inverse_name": inverse_name}
        )
        client.close()
        return [self._convert_result(result) for result in cursor]

    def find_for_bot(self, ifcmodel_id):
        client = ArangoClient(hosts=self._hosts)
        db = client.db(self._db_name, username=self._user, password=self._password)
        aql = db.aql

        query = """
            FOR site IN 1..1 OUTBOUND @ifcmodel_id belongs
            FILTER site.class_name=="IfcSite"

            LET site_building_aggregates = (
                FOR aggregates, decomposed IN 1..1 INBOUND site inverse
                FILTER decomposed.inverse_name=="IsDecomposedBy"
                RETURN aggregates
            )

            LET buildings = (
                FOR aggregates in site_building_aggregates
                FOR building IN 1..1 OUTBOUND aggregates reference
                FILTER building.class_name=="IfcBuilding"
                RETURN building
            )

            LET building_storey_aggregates = (
                FOR building in buildings
                FOR aggregates, decomposed IN 1..1 INBOUND building inverse
                FILTER decomposed.inverse_name=="IsDecomposedBy"
                RETURN aggregates
            )

            LET building_storeies = (
                FOR aggregates in building_storey_aggregates
                FOR storey IN 1..1 OUTBOUND aggregates reference
                FILTER storey.class_name=="IfcBuildingStorey"
                RETURN storey
            )

            LET storey_space_aggregates = (
                FOR storey in building_storeies
                FOR aggregates, decomposed IN 1..1 INBOUND storey inverse
                FILTER decomposed.inverse_name=="IsDecomposedBy"
                RETURN aggregates
            )

            LET storey_spatial_structures = (
                FOR storey in building_storeies
                FOR spatial_structure, contains_elements IN 1..1 INBOUND storey inverse
                FILTER contains_elements.inverse_name=="ContainsElements"
                RETURN spatial_structure
            )

            LET storey_elements = (
                FOR spatial_structure in storey_spatial_structures
                FOR element IN 1..1 OUTBOUND spatial_structure reference
                RETURN element
            )

            LET spaces = (
                FOR aggregates in storey_space_aggregates
                FOR space IN 1..1 OUTBOUND aggregates reference
                FILTER space.class_name=="IfcSpace"
                RETURN space
            )

            LET space_spatial_structures = (
                FOR space in spaces
                FOR spatial_structure, contains_elements IN 1..1 INBOUND space inverse
                FILTER contains_elements.inverse_name=="ContainsElements"
                RETURN spatial_structure
            )

            LET space_elements = (
                FOR spatial_structure in space_spatial_structures
                FOR element IN 1..1 OUTBOUND spatial_structure reference
                RETURN element
            )

            LET space_boundaries = (
                FOR space in spaces
                FOR space_boundary, bounded_by IN 1..1 INBOUND space inverse
                FILTER bounded_by.inverse_name=="BoundedBy"
                RETURN space_boundary
            )

            LET adjacent_element = (
                FOR space_boundary in space_boundaries
                FOR element IN 1..1 OUTBOUND space_boundary reference
                FILTER (
                    element.class_name=="IfcWall" || element.class_name=="IfcWallStandardCase" ||
                    element.class_name=="IfcOpeningElement" || element.class_name=="IfcVirtualElement" ||
                    element.class_name=="IfcDoor")
                RETURN element
            )

            RETURN FLATTEN([
                site, site_building_aggregates, buildings, building_storey_aggregates,
                building_storeies, storey_space_aggregates,storey_spatial_structures,
                storey_elements, spaces, space_spatial_structures,
                space_elements, space_boundaries, adjacent_element
            ])
        """

        cursor = db.aql.execute(
            query,
            bind_vars={"ifcmodel_id": self._ifc_model + "/" + ifcmodel_id}
        )

        result = next(cursor)

        return [self._convert_result(r) for r in result]

    def _convert_result(self, result):
        single_attributes = [
            "integer", "real", "logical", "boolean",
            "enumeration", "string", "reference", "binary"]
        instance_id = result["_key"]
        class_name = result["class_name"]

        def convert_attribute_value(v):
            value_type = v["value_type"]
            if value_type in single_attributes:
                return  IFCAttributeValueDTO(value_type, v["value"])
            elif value_type == "null" or value_type == "omitted":
                return IFCAttributeValueDTO(value_type, None)
            elif value_type == "list":
                return IFCAttributeValueDTO(
                    value_type,
                    [ convert_attribute_value(element) for element in v["value"]])
            else:
                return IFCAttributeValueDTO(value_type, convert_attribute_value(v["value"]))

        attributes = result["attributes"]
        attributedto_list = [
            IFCAttributeDTO(attribute["attribute_name"],
                            convert_attribute_value(attribute["attribute_value"])) for attribute in attributes]
        return IFCInstanceDTO(instance_id, class_name, attributedto_list)

