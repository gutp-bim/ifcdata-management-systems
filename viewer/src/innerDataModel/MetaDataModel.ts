export type MetaDataModel = {
    id: string;
    name: string;
    description: string;
    schemaVersion: string;
};

export const MetaDataModel = {
    make: (id: string, name: string, description: string, schemaVersion: string): MetaDataModel => {
        return {
            id: id,
            name: name,
            description: description,
            schemaVersion: schemaVersion
        }
    }
}