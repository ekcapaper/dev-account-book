import TechGraph from "../components/TechGraph.tsx";
import TechSelectTable from "../components/TechSelectTable.tsx";
import {Space} from "antd";
import TechExplorerTable from "../components/TechExplorerTable.tsx";

function TechEntrySheetPage() {
    return (
        <div>
            <h1>Tech Graph 페이지</h1>
            <TechExplorerTable/>
        </div>
    );
}
export default TechEntrySheetPage;
