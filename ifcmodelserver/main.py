import os
import json
from flask import *
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import configparser
import inject
from command import *
from query import *
from dto import ifcinstances_to_lbd
from infrastructure import ArangoDBIFCModelRepository, ArangoDBIFCModelDAO, ArangoDBIFCInstanceDAO
import setup


UPLOAD_FOLDER = "./uploads"
SWAGGER_URL = "/v1/swagger"
API_URL = "/static/swagger.json"

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={},
)

app.register_blueprint(swaggerui_blueprint)

def app_config(binder):
    binder.bind(IFCModelRepository, ArangoDBIFCModelRepository("config.ini"))
    binder.bind(IFCInstanceDAO, ArangoDBIFCInstanceDAO("config.ini"))
    binder.bind(IFCModelDAO, ArangoDBIFCModelDAO("config.ini"))


config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
baseuri = config["LBD"]["baseuri"]
geomserver_uri = config["LBD"]["geomserver_uri"]


setup.database_setup("config.ini")
inject.configure(app_config)

@app.route("/v1/ifcmodel", methods=["POST"])
def upload_ifc_file():

    handler = IFCModelCommandHandler()
    upload_file = request.files["upfile"]
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], upload_file.filename)
    upload_file.save(filepath)
    modelname = request.form.get("modelname")
    description = request.form.get("description")

    command = UploadIFCModelByStepFile(
        filepath, modelname, description)
    ifcmodel_id = handler.handle(command)

    os.remove(filepath)

    msg = {
        "message": "upload finished",
        "ifcmodel_id": ifcmodel_id.value
    }

    return jsonify(msg)


@app.route("/v1/ifcmodel/<ifcmodelid>", methods=["GET"])
def get_ifcmodel(ifcmodelid):
    handler = IFCModelQueryHandler()
    query = FindIFCModelByID(ifcmodelid)
    result = handler.handle(query)
    dictionary = result.to_dict()
    return jsonify(dictionary)


@app.route("/v1/ifcmodels", methods=["GET"])
def get_ifcmodels():
    handler = IFCModelQueryHandler()
    query = FindAllIFCModels()
    result = handler.handle(query)
    dictionary = [r.to_dict() for r in result]
    return jsonify(dictionary)


@app.route("/v1/ifcinstances/<ifcmodelid>", methods=["GET"])
def get_ifcinstances(ifcmodelid):

    handler = IFCModelQueryHandler()
    query = FindIFCInstancesByIFCModelID(ifcmodelid)
    result = handler.handle(query)

    dictionary = [
        r.to_dict() for r in result
        ]
    return jsonify(dictionary)


@app.route("/v1/ifcinstance/<ifcmodelid>/<guid>", methods=["GET"])
def get_ifcinstance_by_guid(ifcmodelid, guid):
    handler = IFCModelQueryHandler()
    query = FindIFCInstancesByGUID(ifcmodelid, guid)
    result = handler.handle(query)
    return jsonify(result.to_dict())


@app.route("/v1/ifcinstance/<ifcinstanceid>", methods=["GET"])
def get_ifcinstance(ifcinstanceid):

    handler = IFCModelQueryHandler()
    query = FindIFCInstance(ifcinstanceid)
    result = handler.handle(query)

    if result != None:
        dictionary = result.to_dict()
        return jsonify(dictionary)
    else:
        return jsonify({"message": "instance is not found"})


@app.route("/v1/ifcinstances/<ifcmodelid>/<classname>", methods=["GET"])
def get_ifcinstances_by_classname(ifcmodelid, classname):

    handler = IFCModelQueryHandler()
    query = FindIFCInstancesByClassName(ifcmodelid, classname)
    result = handler.handle(query)

    dictionary = [
        r.to_dict() for r in result
    ]

    return jsonify(dictionary)


@app.route("/v1/inverseinstance/<ifcinstanceid>/<inversename>", methods=["GET"])
def get_ifcinstances_by_inverse(ifcinstanceid, inversename):

    handler = IFCModelQueryHandler()
    query = FindIFCInstancesByInverse(ifcinstanceid, inversename)
    result = handler.handle(query)

    dictionary = [
        r.to_dict() for r in result
    ]

    return jsonify(dictionary)



@app.route("/v1/bot/<ifcmodelid>.jsonld", methods=["GET"])
def genereate_bot(ifcmodelid):

    from rdflib import Graph, plugin
    from rdflib.serializer import Serializer

    handler = IFCModelQueryHandler()
    query = FindIFCInstancesForBOT(ifcmodelid)
    result = handler.handle(query)
    lbd_graph = ifcinstances_to_lbd(baseuri, geomserver_uri, ifcmodelid, result)
    json_ld = lbd_graph.serialize(format="json-ld")

    return json_ld


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    CORS(
        app,
        supports_credentials=True
    )
