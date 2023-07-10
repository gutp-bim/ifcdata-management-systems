CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE ifcgeometry
(
  ifcmodel_id character varying NOT NULL,
  guid character varying NOT NULL,
  classname character varying,
  indices integer[],
  vertices float[],
  normals float[],
  face_colors float[][],
  geometry geometry,
  CONSTRAINT ifcgeometry_pkey PRIMARY KEY (ifcmodel_id, guid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE ifcgeometry
  OWNER TO postgres;

CREATE TABLE ifcgeometryglb
(
  ifcmodel_id character varying NOT NULL,
  glb_normal bytea,
  glb_10 bytea,
  glb_40 bytea,
  glb_70 bytea
)
WITH (
  OIDS=FALSE
);
ALTER TABLE ifcgeometryglb
  OWNER TO postgres;