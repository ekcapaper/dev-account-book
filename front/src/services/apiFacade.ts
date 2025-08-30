import {http} from "../lib/fetch.ts";
import type {AccountEntryTree} from "../types/account-entry.ts";
import {DataTypeKind} from "../constants/dataTypeKind.ts";
import {getAccountEntries, getAccountEntry, getAccountRelationships} from "./api.ts";

export const getConvertedFullAccountEntriesAndRelationships = async () => {
    const result = []
    const data = await getAccountEntries();
    for (const entry of data) {
        //console.log(entry)
        result.push({
            key: entry.id + DataTypeKind.Node,
            id: entry.id,
            node_id: entry.id,
            node_title: entry.title,
            connected_node_title: "",
            connected_node_id: "",
            row_data_type: DataTypeKind.Node
        });

        const entry_relationships = await getAccountRelationships(entry.id)
        //console.log(entry_relationships)
        for (const relationship of entry_relationships.outgoing) {
            //console.log(relationship)
            const connectedEntry = await getAccountEntry(relationship.toId);
            //console.log(targetEntry)
            result.push({
                key: entry.title + connectedEntry.id + DataTypeKind.Linked,
                id: connectedEntry.id,
                node_id: entry.id,
                node_title: entry.title,
                connected_node_id: connectedEntry.id,
                connected_node_title: connectedEntry.title,
                row_data_type: DataTypeKind.Linked
            });
        }
    }

    return result;
}

export async function explorerAccountEntryStartLeaf() {
    const start_id = "557c8810-edbf-46ce-86ac-85c306ac75a6";
    return http<AccountEntryTree>(`http://127.0.0.1:8000/v1/account-entries/${start_id}/explore-start-leaf`);
}