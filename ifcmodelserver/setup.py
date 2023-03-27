from arango import ArangoClient
import configparser


def database_setup(file_path: str):

    config = configparser.ConfigParser()
    config.read(file_path)
    hosts = config['DATABASE']['hosts']
    user = config['DATABASE']['user']
    password = config['DATABASE']['password']
    db_name = config['DATABASE']['db_name']
    graph = config['DATABASE']['graph']
    ifc_model = config['DATABASE']['ifc_model']
    ifc_instance = config['DATABASE']['ifc_instance']
    belongs = config['DATABASE']['belongs']
    reference = config['DATABASE']['reference']
    inverse = config['DATABASE']['inverse']

    client = ArangoClient(hosts=hosts)
    sys_db = client.db("_system", username=user, password=password)

    if not sys_db.has_database(db_name):
        db = sys_db.create_database(db_name)
        db = client.db(db_name, username=user, password=password)
        graph = db.create_graph(graph)
        ifc_model_collection = graph.create_vertex_collection(ifc_model)
        ifc_instance_collection = graph.create_vertex_collection(ifc_instance)
        belongs = graph.create_edge_definition(
            edge_collection=belongs,
            from_vertex_collections=[ifc_model],
            to_vertex_collections=[ifc_instance]
        )

        reference = graph.create_edge_definition(
            edge_collection=reference,
            from_vertex_collections=[ifc_instance],
            to_vertex_collections=[ifc_instance]
        )

        inverse = graph.create_edge_definition(
            edge_collection=inverse,
            from_vertex_collections=[ifc_instance],
            to_vertex_collections=[ifc_instance]
        )

        reference.add_fulltext_index(fields=["attribute_name"])
        inverse.add_fulltext_index(fields=["inverse_name"])