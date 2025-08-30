import AccountEntryExplorerTable from "../components/account-entry-explorer-table.tsx";
import AccountEntryExplorerTableReverse from "../components/account-entry-explorer-table-reverse.tsx";

function TechEntrySheetPage() {
    return (
        <div>
            <h1>Tech Graph 페이지</h1>
            <h2>정방향 트리</h2>
            <AccountEntryExplorerTable/>
            <h2>역방향 트리</h2>
            <AccountEntryExplorerTableReverse/>
        </div>
    );
}

export default TechEntrySheetPage;
