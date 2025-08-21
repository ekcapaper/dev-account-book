import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./Layout";
import Home from "./pages/Home";
import About from "./pages/About";
import Profile from "./pages/Profile";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* 공통 레이아웃 */}
                <Route path="/" element={<Layout />}>
                    {/* Outlet 안에 표시될 것들 */}
                    <Route index element={<Home />} />          {/* "/" */}
                    <Route path="about" element={<About />} />  {/* "/about" */}
                    <Route path="profile" element={<Profile />} /> {/* "/profile" */}
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

export default App;
