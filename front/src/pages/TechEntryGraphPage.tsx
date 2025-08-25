import TechGraph from "../components/TechGraph.tsx";
import TechSelectTable from "../components/TechSelectTable.tsx";
import {Space} from "antd";

function TechEntrySheetPage() {
    return (
        <div>
            <h1>Tech Graph 페이지</h1>
            <Space direction={"vertical"}>
                <Space direction={"horizontal"}>
                    <TechSelectTable></TechSelectTable>
                    <TechGraph/>
                </Space>
            </Space>
        </div>
    );
}
export default TechEntrySheetPage;
