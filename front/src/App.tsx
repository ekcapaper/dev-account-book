import {BrowserRouter, Route, Routes} from "react-router-dom";
import Layout from "./Layout";
import Home from "./pages/Home";
import AccountEntrySheetPage from "./pages/account-entry-sheet-page.tsx";
import TechEntryExplorePage from "./pages/account-entry-explore-page.tsx";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* 공통 레이아웃 */}
                <Route path="/" element={<Layout/>}>
                    {/* Outlet 안에 표시될 것들 */}
                    <Route index element={<Home/>}/> {/* "/" */}
                    <Route path={"tech-entry-sheet"} element={<AccountEntrySheetPage/>}/>
                    <Route path={"tech-entry-explore"} element={<TechEntryExplorePage/>}/>
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

export default App;
