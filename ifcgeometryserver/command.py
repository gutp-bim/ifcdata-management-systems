from abc import ABCMeta
import dataclasses
from functools import singledispatch
from domain import create_ifc_file, create_ifc_geometry_data_from_file


class Command(metaclass=ABCMeta):
    """"""


@dataclasses.dataclass(frozen=True)
class StoreIFCGeometryData(Command):
    """"""
    ifc_model_id: str
    file_path: str


class CommandHandler(object):

    def __init__(self, adopter, repository):
        self._adopter = adopter
        self._repository = repository

    def handle(self, command):
        return mutate(command, self._adopter, self._repository)


@singledispatch
def _when(command, adopter, repository):
    raise NotImplementedError("No _when()")


def mutate(command, adopter, repository):
    return _when(command, adopter, repository)

@_when.register(StoreIFCGeometryData)
def _(command, adopter, repository):

    geometry_data_list = create_ifc_geometry_data_from_file(command.ifc_model_id, command.file_path, adopter)

    repository.put(geometry_data_list)

    return True
