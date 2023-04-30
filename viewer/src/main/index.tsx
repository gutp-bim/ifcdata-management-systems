import { BrowserRouter } from "react-router-dom";
import RoutingMain from "pages/RoutingMain";

const View = () => {
    console.log("main")
    return (
        <BrowserRouter>
            <RoutingMain />
        </BrowserRouter>
    )
}

export default View