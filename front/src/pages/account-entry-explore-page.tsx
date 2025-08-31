import AccountEntryExplorerTable from "../components/account-entry-explorer-table.tsx";
import AccountEntryExplorerTableReverse from "../components/account-entry-explorer-table-reverse.tsx";
import AccountEntryExplorerNestedTable from "../components/account-entry-explorer-nested-table.tsx";

function TechEntrySheetPage() {
    return (
        <div>
            <h1>Tech Graph 페이지</h1>
            <h2>설명 테이블</h2>
            <AccountEntryExplorerNestedTable/>
            <h2>정방향 트리</h2>
            <AccountEntryExplorerTable/>
        </div>
    );
}

export default TechEntrySheetPage;
