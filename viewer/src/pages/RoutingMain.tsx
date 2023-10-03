import {Suspense} from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import ModelListPage from "pages/list";
import ModelViewPage from "pages/view"

export const RoutingMain = () => {
    console.log("route called")
    return (
        <Suspense fallback={null}>
            <Routes>
                <Route path="/models/list" element={<ModelListPage />} />
                <Route path="/models/item/:modelId/view/:lod" element={<ModelViewPage />} />
                <Route path="/models" element={<Navigate to="/models/list" replace />} />
                <Route path="*" element={<Navigate to="/models" replace />} />
            </Routes>
        </Suspense>
    )
}

export default RoutingMain;