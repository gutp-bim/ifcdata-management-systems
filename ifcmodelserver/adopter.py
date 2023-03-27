from model import *
import ifcopenshell


class IFCOpenshellIFCModelAdopter(IFCModelAdopter):

    def generate_ifcmodel(self, modelname: str, description: str, file_path: str) -> IFCModel:

        ifc_file = ifcopenshell.open(file_path)
        id_table = {instance.id() :IFCInstanceRepository.next_identity() for instance in ifc_file}

        def convert_ifcentity(e) -> IFCInstance:
            info = e.get_info()
            tmp_id = info["id"]
            classname = info["type"]

            def convert_attribute_value(attribute_type, value) -> IFCAttributeValue:

                if value == None:
                    if attribute_type == "DERIVED":
                        return IFCOmittedValue()
                    else:
                        return IFCNullValue()
                else:
                    if attribute_type == "INT":
                        return IFCIntegerValue(value)
                    elif attribute_type == "DOUBLE":
                        return IFCRealValue(value)
                    elif attribute_type == "BOOL":
                        return IFCBooleanlValue(value)
                    elif attribute_type == "STRING":
                        return IFCStringValue(value)
                    elif attribute_type == "ENUMERATION":
                        return IFCEnumerationValue(value)
                    elif attribute_type == "LOGICAL":
                        return IFCLogicalValue(value)
                    elif attribute_type == "ENTITY INSTANCE":
                        if value.id() == 0:
                            type_name = value.is_a()
                            return IFCTypedValue(
                                type_name, convert_attribute_value(value.attribute_type(0), value[0]))
                        else:
                            return IFCReferenceValue(id_table[value.id()])
                    elif "AGGREGATE OF" in attribute_type:
                        return IFCListValue([convert_attribute_value(attribute_type[13:], v) for v in value])

            attributes = [
                IFCAttribute(IFCAttributeName(e.attribute_name(i)),
                convert_attribute_value(e.attribute_type(i), attribute)
                ) for i, attribute in enumerate(e)]

            inverse_names = e.wrapped_data.get_inverse_attribute_names()
            inverses = [
                IFCInverse(
                    IFCInverseName(inverse_name),
                    [id_table[reference.id()] for reference in getattr(e, inverse_name)]
                )   for inverse_name in inverse_names]

            return IFCInstance(id_table[tmp_id], IFCClassName(classname), attributes, inverses)

        instances =  [convert_ifcentity(instance) for instance in ifc_file]

        return create_ifcmodel(ifc_file.schema, modelname, description,instances)
