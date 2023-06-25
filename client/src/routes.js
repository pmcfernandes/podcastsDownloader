import { Routes, Route, BrowserRouter } from "react-router-dom";
import Home from "./pages/Home";


const Router = () => {
    return (
        <BrowserRouter>
            <Routes>
                <Route element={<Home />} path="/" exact />
            </Routes>
        </BrowserRouter>
    )
}

export default Router;