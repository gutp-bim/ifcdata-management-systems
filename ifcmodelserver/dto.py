import dataclasses
from typing import List, Any

@dataclasses.dataclass(frozen=True)
class IFCModelDTO(object):

    ifcmodel_id: str
    schema_version: str
    model_name: str
    description: str

    def to_dict(self):
        return {
            "ifcmodel_id": self.ifcmodel_id,
            "schema_version": self.schema_version,
            "model_name": self.model_name,
            "description": self.description
        }


@dataclasses.dataclass(eq=True, frozen=True)
class IFCAttributeValueDTO(object):

    value_type: str
    value: Any

    def to_dict(self):
        single_attributes = [
            "integer", "real", "logical", "boolean",
            "enumeration", "string", "reference", "binary"]
        if self.value_type == "list":
            return {
                "value_type": self.value_type,
                "value": [ v.to_dict() for v in self.value]
            }
        elif self.value_type == "omitted" or self.value_type == "null":
            return {
                "value_type": self.value_type
            }
        elif self.value_type in single_attributes:
            return {
                "value_type": self.value_type,
                "value": self.value
            }
        else:
            return {
                "value_type": self.value_type,
                "value": self.value.to_dict()
            }

@dataclasses.dataclass(eq=True, frozen=True)
class IFCAttributeDTO(object):

    attribute_name: str
    value: IFCAttributeValueDTO

    def to_dict(self):
        return {
            "attribute_name": self.attribute_name,
            "value": self.value.to_dict()
        }


@dataclasses.dataclass(eq=True, frozen=True)
class IFCInstanceDTO(object):

    ifcinstance_id: str
    classname: str
    attribute_values: List[IFCAttributeDTO]

    def get_value(self, attribute_name):
        result = [a for a in self.attribute_values if a.attribute_name == attribute_name]
        if len(result) == 0:
            return None
        else:
            return result[0]

    def to_dict(self):
        return {
            "instance_id": self.ifcinstance_id,
            "classname": self.classname,
            "attribute_values": [
                attribute.to_dict() for attribute in self.attribute_values
            ]
        }

    def __hash__(self):
        return hash(self.ifcinstance_id)


from rdflib import Graph, Literal, BNode, RDF, RDFS, URIRef
from rdflib.namespace import Namespace

BOT = Namespace("https://w3id.org/bot#")
IFC4 = Namespace("http://www.buildingsmart-tech.org/IFC4#")

def ifcinstances_to_lbd(baseuri:str, geomserver_uri:str, ifcmodelid:str, instances:List[IFCInstanceDTO]):

    graph = Graph()
    graph.bind("bot", BOT)
    baseuri_namespace = Namespace(baseuri)
    graph.bind("inst", baseuri_namespace)
    graph.bind("ifc4", IFC4)

    id_dict = {instance.ifcinstance_id: instance for instance in instances}
    classname_dict = {}

    for instance in instances:
        classname = instance.classname
        if classname in classname_dict:
            instance_dict = classname_dict[classname]
            instance_dict[instance.ifcinstance_id] = instance
            classname_dict[classname] = instance_dict
        else:
            classname_dict[classname] = {instance.ifcinstance_id: instance}

    site_dict = classname_dict["IfcSite"]
    rel_aggregates_dict = classname_dict["IfcRelAggregates"]
    rel_contained_spatial_structure_dict = classname_dict["IfcRelContainedInSpatialStructure"]


    def proc_zone_and_elements(space_uri, element):

        if element.classname=="IfcSpatialZone":
            zone_uri = URIRef(baseuri + "spatial_zone_" + element.ifcinstance_id)
            graph.add((space_uri, BOT.hasSpace, zone_uri))
            graph.add((zone_uri, RDF.type, BOT.Space))
            global_id = element.get_value("GlobalId")
            graph.add((zone_uri, IFC4.GlobalId, Literal(global_id.value.value)))
            graph.add((zone_uri, IFC4.Class, Literal(element.classname)))
            zone_3dmodel_uri = geomserver_uri + "ifcgeometry/" + ifcmodelid + "/" + global_id.value.value
            graph.add((zone_uri, BOT.has3DModel, Literal(zone_3dmodel_uri)))

            name = element.get_value("Name")
            if name != None and name.value.value_type != "null":
                graph.add((zone_uri, IFC4.Name, Literal(name.value.value)))

            long_name = element.get_value("LongName")
            if long_name != None and long_name.value.value_type != "null":
                graph.add((zone_uri, IFC4.LongName, Literal(long_name.value.value)))

        else:
            element_uri = URIRef(baseuri + "element_" + element.ifcinstance_id)
            graph.add((space_uri, BOT.hasElement, element_uri))
            graph.add((element_uri, RDF.type, BOT.Element))
            graph.add((element_uri, IFC4.Class, Literal(element.classname)))
            global_id = element.get_value("GlobalId")
            graph.add((element_uri, IFC4.GlobalId, Literal(global_id.value.value)))
            element_3dmodel_uri = geomserver_uri + "ifcgeometry/" + ifcmodelid + "/" + global_id.value.value
            graph.add((element_uri, BOT.has3DModel, Literal(element_3dmodel_uri)))
            name = element.get_value("Name")
            if name != None and name.value.value_type != "null":
                graph.add((element_uri, IFC4.Name, Literal(name.value.value)))

            long_name = element.get_value("LongName")
            if long_name != None and long_name.value.value_type != "null":
                graph.add((element_uri, IFC4.LongName, Literal(long_name.value.value)))

    """
    def proc_storey_element(building_storey_uri, element):
        element_uri = URIRef(baseuri + "element_" + element.ifcinstance_id)
        graph.add((building_storey_uri, BOT.hasElement, element_uri))
        graph.add((element_uri, RDF.type, BOT.Element))
        global_id = element.get_value("GlobalId")
        graph.add((element_uri, IFC4.GlobalId, Literal(global_id.value.value)))
        element_3dmodel_uri = geomserver_uri + "ifcgeometry/" + ifcmodelid + "/" + global_id
        graph.add((element_uri, BOT.has3DModel, Literal(element_3dmodel_uri)))
    """

    def proc_storey_space(building_storey_uri, space):
        space_uri = URIRef(baseuri + "space_" + space.ifcinstance_id)
        graph.add((building_storey_uri, BOT.hasSpace, space_uri))
        graph.add((space_uri, RDF.type, BOT.Space))
        global_id = space.get_value("GlobalId")
        graph.add((space_uri, IFC4.GlobalId, Literal(global_id.value.value)))
        space_3dmodel_uri = geomserver_uri + "ifcgeometry/" + ifcmodelid + "/" + global_id.value.value
        graph.add((space_uri, BOT.has3DModel, Literal(space_3dmodel_uri)))
        graph.add((space_uri, IFC4.Class, Literal(space.classname)))

        name = space.get_value("Name")
        if name != None and name.value.value_type != "null":
            graph.add((space_uri, IFC4.Name, Literal(name.value.value)))

        long_name = space.get_value("LongName")
        if long_name != None and long_name.value.value_type != "null":
            graph.add((space_uri, IFC4.LongName, Literal(long_name.value.value)))

        space_contained_spatial_structure = [
            v for k, v in rel_contained_spatial_structure_dict.items()
            if  space.ifcinstance_id in v.get_value("RelatingStructure").value.value]

        for rel_contained_spatial_structure in space_contained_spatial_structure:
            related_elements = rel_contained_spatial_structure.get_value("RelatedElements")
            for v in related_elements.value.value:
                element = id_dict[v.value]
                proc_zone_and_elements(space_uri, element)


    def proc_building_storey(building_uri, building_storey):
        building_storey_uri = URIRef(baseuri + "building_storey_" + building_storey.ifcinstance_id)
        graph.add((building_uri, BOT.hasStorey, building_storey_uri))
        graph.add((building_storey_uri, RDF.type, BOT.Storey))
        global_id = building_storey.get_value("GlobalId")
        graph.add((building_storey_uri, IFC4.GlobalId, Literal(global_id.value.value)))
        graph.add((building_storey_uri, IFC4.Class, Literal(building_storey.classname)))

        name = building_storey.get_value("Name")
        if name != None and name.value.value_type != "null":
            graph.add((building_storey_uri, IFC4.Name, Literal(name.value.value)))

        long_name = building_storey.get_value("LongName")
        if long_name != None and long_name.value.value_type != "null":
            graph.add((building_storey_uri, IFC4.LongName, Literal(long_name.value.value)))
        space_aggregates = [v for k, v in rel_aggregates_dict.items() if  building_storey.ifcinstance_id in v.get_value("RelatingObject").value.value]

        for aggregates in space_aggregates:
            related_objects = aggregates.get_value("RelatedObjects")
            for v in related_objects.value.value:
                space = id_dict[v.value]
                proc_storey_space(building_storey_uri, space)

        storey_contained_spatial_structure = [
            v for k, v in rel_contained_spatial_structure_dict.items()
            if  building_storey.ifcinstance_id in v.get_value("RelatingStructure").value.value]

        for rel_contained_spatial_structure in storey_contained_spatial_structure:
            related_elements = rel_contained_spatial_structure.get_value("RelatedElements")
            for v in related_elements.value.value:
                element = id_dict[v.value]
                proc_zone_and_elements(building_storey_uri, element)


    def proc_building(site_uri, building):
        building_uri = URIRef(baseuri + "building_" + building.ifcinstance_id)
        graph.add((site_uri, BOT.hasBuilding, building_uri))
        graph.add((building_uri, RDF.type, BOT.Building))
        global_id = building.get_value("GlobalId")
        graph.add((building_uri, IFC4.GlobalId, Literal(global_id.value.value)))
        graph.add((building_uri, IFC4.Class, Literal((building.classname))))
        name = building.get_value("Name")
        if name != None and name.value.value_type != "null":
            graph.add((building_uri, IFC4.Name, Literal(name.value.value)))

        long_name = building.get_value("LongName")
        if long_name != None and long_name.value.value_type != "null":
            graph.add((building_uri, IFC4.LongName, Literal(long_name.value.value)))

        description = building.get_value("Description")
        if description.value.value_type != "null":
            graph.add((building_uri, IFC4.Description, Literal(description.value.value)))

        storey_aggregates = [v for k, v in rel_aggregates_dict.items() if  building.ifcinstance_id in v.get_value("RelatingObject").value.value]
        for aggregates in storey_aggregates:
            related_objects = aggregates.get_value("RelatedObjects")

            for v in related_objects.value.value:
                building_storey = id_dict[v.value]
                proc_building_storey(building_uri, building_storey)


    def proc_site():
        for instance_id, site in site_dict.items():
            site_uri = URIRef(baseuri + "site_" + instance_id)
            global_id = site.get_value("GlobalId")
            graph.add((site_uri, RDF.type, BOT.Site))
            graph.add((site_uri, IFC4.GlobalId, Literal(global_id.value.value)))
            graph.add((site_uri, IFC4.Class, Literal(site.classname)))

            name = site.get_value("Name")
            if name != None and name.value.value_type != "null":
                graph.add((site_uri, IFC4.Name, Literal(name.value.value)))

            ref_latitude = site.get_value("RefLatitude")
            if ref_latitude.value.value_type != "null":
                value = [ v.value for v in ref_latitude.value.value]
                graph.add((site_uri, IFC4.RefLatitude, Literal(value)))

            ref_longitude = site.get_value("RefLongitude")
            if ref_longitude.value.value_type != "null":
                value = [ v.value for v in ref_longitude.value.value]
                graph.add((site_uri, IFC4.RefLongitude, Literal(value)))

            ref_elevation = site.get_value("RefElevation")
            if ref_elevation.value.value_type != "null":
                graph.add((site_uri, IFC4.RefElevation, Literal(ref_elevation.value.value)))

            long_name = site.get_value("LongName")
            if long_name != None and long_name.value.value_type != "null":
                graph.add((site_uri, IFC4.LongName, Literal(long_name.value.value)))

            description = site.get_value("Description")
            if description.value.value_type != "null":
                graph.add((site_uri, IFC4.Description, Literal(description.value.value)))

            site_aggregates = [
                v for k, v in rel_aggregates_dict.items()
                if  instance_id in v.get_value("RelatingObject").value.value]

            for aggregates in site_aggregates:
                related_objects = aggregates.get_value("RelatedObjects")

                for v in related_objects.value.value:
                    building = id_dict[v.value]
                    proc_building(site_uri, building)
    proc_site()

    return graph