export type Routing<T> = {
    route: string;
    buildURL: (props: T) => string;
};

export const Routing = {
    simple: (route: string): Routing<void> => ({
        route: route,
        buildURL: () => route,
    }),
    parameterized: <T>(route: string, builder: (props: T) => string): Routing<T> => ({
        route: route,
        buildURL: builder
    }),
};

export type ModelViewPageProps = { modelId: string };

export const routes = {
    root: Routing.simple("/"),

    models: {
        index: Routing.simple("/models"),
        list: Routing.simple("/models/list"),
        item: {
            view: Routing.parameterized<ModelViewPageProps>(
                "/models/item/:modelId/view",
                ({modelId}) => `/models/item/${modelId}/view`
            )
        },
    },
};