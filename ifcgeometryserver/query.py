from abc import ABCMeta
import dataclasses
from functools import singledispatch


class Query(metaclass=ABCMeta):
    """"""


@dataclasses.dataclass(frozen=True)
class GetGeometryDataByIFCModelId(Query):
    """"""
    ifcmodel_id: str


@dataclasses.dataclass(frozen=True)
class GetGeometryDataByGlobalId(Query):
    """"""
    ifcmodel_id: str
    global_id: str


@dataclasses.dataclass(frozen=True)
class GetGeometryDataByClassName(Query):
    """"""
    ifcmodel_id: str
    class_name: str


@dataclasses.dataclass(frozen=True)
class GetGeometryDataGlbByIFCModelId(Query):
    """"""
    ifcmodel_id: str


class QueryHandler(object):

    def __init__(self, dao):
        self._dao = dao

    def handle(self, command):
        return mutate(command, self._dao)


@singledispatch
def _when(command, repository):
    raise NotImplementedError("No _when()")


def mutate(command, dao):
    return _when(command, dao)

@_when.register(GetGeometryDataByIFCModelId)
def _(command, dao):
    return dao.find_by_ifcmodel_id(command.ifcmodel_id)


@_when.register(GetGeometryDataByClassName)
def _(command, dao):
    return dao.find_by_class_name(command.ifcmodel_id, command.class_name)


@_when.register(GetGeometryDataByGlobalId)
def _(command, dao):
    return dao.find_by_global_id(command.ifcmodel_id, command.global_id)


@_when.register(GetGeometryDataGlbByIFCModelId)
def _(command, dao):
    return dao.find_glb_by_ifcmodel_id(command.ifcmodel_id)