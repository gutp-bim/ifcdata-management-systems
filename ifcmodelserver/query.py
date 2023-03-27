import dataclasses
from functools import singledispatch
from abc import ABCMeta
import inject
from model import IFCModelDAO, IFCInstanceDAO



class IFCModelQuery(object):

    __metaclass__ = ABCMeta


class FindAllIFCModels(object):

    pass


class FindIFCModelByID(IFCModelQuery):

    def __init__(self, ifcmodel_id):
        self._ifcmodel_id = ifcmodel_id

    @property
    def ifcmodel_id(self):
        return self._ifcmodel_id


class FindIFCInstancesByIFCModelID(IFCModelQuery):

    def __init__(self, ifcmodel_id):
        self._ifcmodel_id = ifcmodel_id

    @property
    def ifcmodel_id(self):
        return self._ifcmodel_id


class FindIFCInstance(IFCModelQuery):

    def __init__(self, ifcinstance_id):
        self._ifcinstance_id = ifcinstance_id

    @property
    def ifcinstance_id(self):
        return self._ifcinstance_id


class FindIFCInstancesByClassName(IFCModelQuery):

    def __init__(self, ifcmodel_id, classname):
        self._ifcmodel_id = ifcmodel_id
        self._classname = classname

    @property
    def ifcmodel_id(self):
        return self._ifcmodel_id

    @property
    def classname(self):
        return self._classname


class FindIFCInstancesByGUID(IFCModelQuery):

    def __init__(self, ifcmodel_id, guid):
        self._ifcmodel_id = ifcmodel_id
        self._guid =  guid

    @property
    def ifcmodel_id(self):
        return self._ifcmodel_id

    @property
    def guid(self):
        return self._guid



class FindIFCInstancesByInverse(IFCModelQuery):

    def __init__(self, ifcinstance_id, inverse_name):
        self._ifcinstance_id = ifcinstance_id
        self._inverse_name = inverse_name

    @property
    def ifcinstance_id(self):
        return self._ifcinstance_id

    @property
    def inverse_name(self):
        return self._inverse_name

######下記からはLBD生成のためのクエリ######

class FindIFCInstancesForBOT(IFCModelQuery):

    def __init__(self, ifcmodel_id):
        self._ifcmodel_id = ifcmodel_id

    @property
    def ifcmodel_id(self):
        return self._ifcmodel_id


########################################################
# IFCModelQueryのHandler
########################################################


class IFCModelQueryHandler(object):

    _model_dao = inject.attr(IFCModelDAO)
    _instance_dao = inject.attr(IFCInstanceDAO)


    def handle(self, query):
        return mutate(query, self._model_dao, self._instance_dao)


def mutate(query, model_dao, instance_dao):
    return _when(query, model_dao, instance_dao)


@singledispatch
def _when(query, model_dao, instance_dao):
    """Modify an entity (usually an aggregate root) by replaying an event."""
    raise NotImplementedError("No _when()")


@_when.register(FindAllIFCModels)
def _find_all(query, model_dao, instance_dao):
    return model_dao.find_all()


@_when.register(FindIFCModelByID)
def _find_by_ifcmodelid(query, model_dao, instance_dao):
    return model_dao.find_by_ifcmodelid(query.ifcmodel_id)


@_when.register(FindIFCInstancesByIFCModelID)
def _find_all_ifcinstances(query, model_dao, instance_dao):
    return instance_dao.find_all(query.ifcmodel_id)


@_when.register(FindIFCInstance)
def _find_ifcinstance_by_ifcinstanceid(query, model_dao, instance_dao):
    return instance_dao.find_by_ifcinstanceid(query.ifcinstance_id)


@_when.register(FindIFCInstancesByClassName)
def _find_ifcinstances_by_classname(query, model_dao, instance_dao):
    return instance_dao.find_by_classname(
        query.ifcmodel_id, query.classname
    )


@_when.register(FindIFCInstancesByGUID)
def _find_by_guid(query, model_dao, instance_dao):
    return instance_dao.find_by_guid(query.ifcmodel_id, query.guid)


@_when.register(FindIFCInstancesByInverse)
def _find_ifcinstances_by_inverse(query, model_dao, instance_dao):
    return instance_dao.find_by_inverse_name(
        query.ifcinstance_id, query.inverse_name
    )

@_when.register(FindIFCInstancesForBOT)
def _find_ifcinstances_for_bot(query, model_dao, instance_dao):
    return instance_dao.find_for_bot(query.ifcmodel_id)
