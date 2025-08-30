import {BrowserRouter, Route, Routes} from "react-router-dom";
import Layout from "./Layout";
import Home from "./pages/Home";
import TechEntrySheetPage from "./pages/TechEntrySheetPage.tsx";
import TechEntryExplorePage from "./pages/TechEntryExplorePage.tsx";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* 공통 레이아웃 */}
                <Route path="/" element={<Layout/>}>
                    {/* Outlet 안에 표시될 것들 */}
                    <Route index element={<Home/>}/> {/* "/" */}
                    <Route path={"tech-entry-sheet"} element={<TechEntrySheetPage/>}/>
                    <Route path={"tech-entry-explore"} element={<TechEntryExplorePage/>}/>
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

export default App;
