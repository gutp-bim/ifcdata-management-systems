from functools import singledispatch
from abc import ABCMeta
import dataclasses
import inject
from adopter import IFCOpenshellIFCModelAdopter
from model import IFCModelRepository


class IFCModelCommand(object):

    __metaclass__ = ABCMeta


@dataclasses.dataclass(frozen=True)
class UploadIFCModelByStepFile(IFCModelCommand):

    file_path: str
    modelname: str
    description: str


#############################################################################
# コマンドに応じた処理を行うハンドラークラス
#############################################################################


class IFCModelCommandHandler(object):

    _repository = inject.attr(IFCModelRepository)

    def handle(self, command):
        return mutate(command, self._repository)


def mutate(command, repository):
    return _when(command, repository)


@singledispatch
def _when(command, repository):
    raise NotImplementedError("No _when()")


@_when.register(UploadIFCModelByStepFile)
def _(command, repository):

    adopter = IFCOpenshellIFCModelAdopter()
    ifc_model = adopter.generate_ifcmodel(command.modelname, command.description, command.file_path)
    return repository.put(ifc_model)