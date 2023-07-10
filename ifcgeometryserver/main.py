import os
from flask import *
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import configparser
from command import CommandHandler, StoreIFCGeometryData, DeleteIFCGeometryData
from query import (
    QueryHandler, GetGeometryDataByIFCModelId,
    GetGeometryDataByClassName, GetGeometryDataByGlobalId, GetGeometryDataGlbByIFCModelId)
from dto import export_glb
from infrastructure import IfcOpenShellIfcFileAdopter, PostgreSQLIfcGeometryDataDAO, PostgreSQLIfcGeometryDataRepository


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

config = configparser.ConfigParser()
config.read("./config.ini", encoding="utf-8")
host = config["database"]["host"]
port = int(config["database"]["port"])
database = config["database"]["database_name"]
user = config["database"]["user"]
password = config["database"]["password"]

repository = PostgreSQLIfcGeometryDataRepository(
        host=host, port=port, database=database, user=user, password=password)
dao = PostgreSQLIfcGeometryDataDAO(
        host=host, port=port, database=database, user=user, password=password)
adopter = IfcOpenShellIfcFileAdopter()


@app.route("/v1/ifcgeometry/<ifcmodel_id>", methods=["GET"])
def get_all_geometries(ifcmodel_id):
    query = None
    query_handler = QueryHandler(dao)
    class_name = request.args.get("class")
    if class_name != None:
        query = GetGeometryDataByClassName(ifcmodel_id, class_name)
    else:
        query = GetGeometryDataByIFCModelId(ifcmodel_id)
    result = query_handler.handle(query)
    message = {"geometries": [r.to_json() for r in result]}
    return jsonify(message)


@app.route("/v1/ifcgeometry/<ifcmodel_id>.glb", defaults={'lod': None}, methods=["GET"])
@app.route("/v1/ifcgeometry/<ifcmodel_id>.glb/<lod>", methods=["GET"])
def get_all_geometries_glb(ifcmodel_id, lod):
    query = None
    query_handler = QueryHandler(dao)
    if lod:
        query = GetGeometryDataGlbByIFCModelId(ifcmodel_id, int(lod))
    else:
        query = GetGeometryDataGlbByIFCModelId(ifcmodel_id, 4)
    result = query_handler.handle(query)
    return result


@app.route("/v1/ifcgeometry/<ifcmodel_id>/<global_id>", methods=["GET"])
def get_geometries_by_guid(ifcmodel_id, global_id):
    query_handler = QueryHandler(dao)
    query = GetGeometryDataByGlobalId(ifcmodel_id, global_id)
    result = query_handler.handle(query)
    message = {"geometries": result.to_json()}
    return jsonify(message)


@app.route("/v1/ifcgeometry/upload", methods=["POST"])
def upload_ifc_file():
    handler = CommandHandler(adopter, repository)
    upload_file = request.files["upfile"]
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], upload_file.filename)
    upload_file.save(filepath)
    ifcmodel_id = request.form.get("ifcmodel_id")

    command = StoreIFCGeometryData(ifcmodel_id, filepath)

    handler.handle(command)

    os.remove(filepath)

    msg = {
        "message": "upload finished",
    }

    return jsonify(msg)

@app.route("/v1/ifcgeometry/<ifcmodel_id>", methods=["DELETE"])
def delete_ifcmodel(ifcmodel_id):
    handler = CommandHandler(adopter, repository)
    command = DeleteIFCGeometryData(ifcmodel_id)
    handler.handle(command)

    msg = {
        "message": "delete finished"
    }

    return jsonify(msg)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
    CORS(
        app,
        supports_credentials=True
    )
