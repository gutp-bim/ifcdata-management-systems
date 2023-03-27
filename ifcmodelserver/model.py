import uuid
from itertools import chain
from abc import ABCMeta, abstractmethod
from typing import List
import dataclasses


class Entity:
    """全てのドメインオブジェクトの基底クラス"""

    __metaclass__ = ABCMeta


class ValueObject:
    """全ての値オブジェクトの基底クラス"""

    __metaclass__ = ABCMeta


### IFCのインスタンスの定義


@dataclasses.dataclass(frozen=True)
class IFCInstanceId(ValueObject):

    value: str


@dataclasses.dataclass(frozen=True)
class IFCClassName(ValueObject):

    value :str


@dataclasses.dataclass(frozen=True)
class IFCAttributeName(ValueObject):

    value :str


## IFCの属性値オブジェクト

class IFCAttributeValue(ValueObject):
    """属性値のオブジェクトの基底クラス"""

    __metaclass__ = ABCMeta


@dataclasses.dataclass(frozen=True)
class IFCIntegerValue(IFCAttributeValue):

    u"""
    IFCの整数型属性値を表すクラス
    """

    value: int

    def to_dict(self):
        return {
            "value_type": "integer",
            "value": self.value
        }


@dataclasses.dataclass(frozen=True)
class IFCRealValue(IFCAttributeValue):

    u"""
    IFCの浮動小数点型を表すクラス
    """

    value: float

    def to_dict(self):
        return {
            "value_type": "real",
            "value": self.value
        }


@dataclasses.dataclass(frozen=True)
class IFCLogicalValue(IFCAttributeValue):

    u"""
    IFCの論理型を表すクラス
    """

    value: str

    def to_dict(self):
        return {
            "value_type": "logical",
            "value": self.value
        }


@dataclasses.dataclass(frozen=True)
class IFCBooleanlValue(IFCAttributeValue):

    u"""
    IFCの論理型を表すクラス
    """

    value: bool

    def to_dict(self):
        return {
            "value_type": "boolean",
            "value": self.value
        }


@dataclasses.dataclass(frozen=True)
class IFCEnumerationValue(IFCAttributeValue):

    u"""
    IFCの列挙型の値を表すクラス
    """

    value: str

    def to_dict(self):
        return {
            "value_type": "enumeration",
            "value": self.value
        }


@dataclasses.dataclass(frozen=True)
class IFCStringValue(IFCAttributeValue):

    u"""
    IFCの文字列型の値を表すクラス
    """

    value : str

    def to_dict(self):
        return {
            "value_type": "string",
            "value": self.value
        }


@dataclasses.dataclass(frozen=True)
class IFCReferenceValue(IFCAttributeValue):

    u"""
    IFCの参照型を値表すクラス
    """

    value : IFCInstanceId

    def to_dict(self):
        return {
            "value_type": "reference",
            "value": self.value.value
        }


@dataclasses.dataclass(frozen=True)
class IFCBinaryValue(IFCAttributeValue):

    u"""
    IFCのバイナリ型の値を表すクラス
    """

    value: str

    def to_dict(self):
        return {
            "value_type": "binary",
            "value": self.value
        }


@dataclasses.dataclass(frozen=True)
class IFCListValue(IFCAttributeValue):

    u"""
    IFCのリスト型の値を表すクラス
    """

    value: List[IFCAttributeValue]

    def to_dict(self):
        return {
            "value_type": "list",
            "value": [v.to_dict() for v in self.value]
        }


@dataclasses.dataclass(frozen=True)
class IFCTypedValue(IFCAttributeValue):

    u"""
    IFCの独自定義型データの値を表すクラス
    """

    type_name: str
    value: IFCAttributeValue

    def to_dict(self):
        return {
            "value_type": self.type_name,
            "value": self.value.to_dict()
        }


@dataclasses.dataclass(frozen=True)
class IFCOmittedValue(IFCAttributeValue):

    u"""
    IFCにおけるNULLの値を表すクラス
    """

    def to_dict(self):
        return {"value_type": "omitted"}


@dataclasses.dataclass(frozen=True)
class IFCNullValue(IFCAttributeValue):

    u"""
    IFCにおけるNULLの値を表すクラス
    """

    def to_dict(self):
        return {"value_type": "null"}


@dataclasses.dataclass(frozen=True)
class IFCAttribute(ValueObject):

    attribute_name: IFCAttributeName
    attribute_value: IFCAttributeValue

    def to_dict(self):
        return {
            "attribute_name": self.attribute_name.value,
            "attribute_value": self.attribute_value.to_dict()
        }


@dataclasses.dataclass(frozen=True)
class IFCInverseName(ValueObject):

    value: str


@dataclasses.dataclass(frozen=True)
class IFCInverse(ValueObject):

    inverse_name: IFCInverseName
    value: List[IFCInstanceId]


@dataclasses.dataclass(frozen=True)
class IFCInstance(Entity):

    instance_id: IFCInstanceId
    classname: IFCClassName
    attributes: List[IFCAttribute]
    inverses: List[IFCInverse]

    def get_references(self):
        result = []

        for attribute in self.attributes:
            v = attribute.attribute_value

            if isinstance(v, IFCReferenceValue):
                result.append((attribute.attribute_name, v))

            elif isinstance(v, IFCListValue):
                for element in v.value:
                    if isinstance(element, IFCReferenceValue):
                        result.append((attribute.attribute_name, element))

        return result


    def to_dict(self):
        return {
            "instance_id": self.instance_id.value,
            "classname": self.classname.value,
            "attributes": [ attribute.to_dict() for attribute in self.attributes ]
        }


### IFCモデルの定義

@dataclasses.dataclass(frozen=True)
class IFCModelId(ValueObject):

    value: str


@dataclasses.dataclass(frozen=True)
class ModelName(ValueObject):

    value: str


@dataclasses.dataclass(frozen=True)
class SchemaVersion(ValueObject):

    value: str


@dataclasses.dataclass(frozen=True)
class Description(ValueObject):

    value: str


@dataclasses.dataclass(frozen=True)
class IFCModel(Entity):

    ifcmodel_id: IFCModelId
    model_name: ModelName
    schema_version: SchemaVersion
    description: Description
    instances: List[IFCInstance]



# ======================================================================================================================
# IFCModelのファクトリ
#


def create_ifcmodel(schema_version :str,
                    model_name: str,
                    description: str,
                    instances: List[IFCInstance]) -> IFCModel:

    ifc_model_id = IFCModelRepository.next_identity()

    return IFCModel(ifc_model_id,
                    ModelName(model_name),
                    SchemaVersion(schema_version),
                    Description(description),
                    instances)



# ======================================================================================================================
# IFCModelのリポジトリ
#


class IFCModelRepository:

    __metaclass__ = ABCMeta

    @staticmethod
    def next_identity() -> IFCModelId:
        return IFCModelId(str(uuid.uuid4().hex))

    @abstractmethod
    def put(self, a_ifcmodel: IFCModel):
        pass

    @abstractmethod
    def remove_by_ifcmodelid(self, a_ifcmodel_id: IFCModelId):
        pass


# ======================================================================================================================
# IFCModelのアダプタ
#

class IFCModelAdopter:

    __metaclass__ = ABCMeta

    def generate_ifcmodel(self, modelname, description, file_path: str) -> IFCModel:
        pass


class IFCInstanceRepository:

    __metaclass__ = ABCMeta

    @staticmethod
    def next_identity() -> IFCInstanceId:
        return IFCInstanceId(str(uuid.uuid4().hex))


#####################################################################################################
#
#####################################################################################################

class IFCModelDAO:

    __metaclass__ = ABCMeta

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def find_by_ifcmodelid(self, ifcmodelid):
        pass



class IFCInstanceDAO:

    __metaclass__ = ABCMeta

    @abstractmethod
    def find_all(self, ifcmodel_id):
        pass

    @abstractmethod
    def find_by_ifcinstanceid(self, ifcinstanceid):
        pass

    @abstractmethod
    def find_by_classname(self, ifcmodel_id, class_name):
        pass

    @abstractmethod
    def find_by_inverse_name(self, ifcinstance_id, inverse_name):
        pass

    @abstractmethod
    def find_by_guid(self, ifcmodel_id, guid):
        pass

    @abstractmethod
    def find_for_bot(self, ifcmodel_id):
        pass