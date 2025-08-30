import {http} from "../lib/fetch.ts";
import type {AccountEntryTree} from "../types/account-entry.ts";
import {SheetDataTypeKind} from "../constants/sheet-data-type-kind.ts";
import {getAccountEntries, getAccountEntry, getAccountRelationships} from "./account-entry-api.ts";
import type {AccountEntryTableDataType} from "../types/account-entry-table-data-type.ts";

export const getConvertedFullAccountEntriesAndRelationships: () => Promise<AccountEntryTableDataType[]> = async () => {
    const result : AccountEntryTableDataType[] = [];
    const data = await getAccountEntries();
    for (const entry of data) {
        //console.log(entry)
        result.push({
            key: entry.id + SheetDataTypeKind.Node,
            id: entry.id,
            node_id: entry.id,
            node_title: entry.title,
            node_desc: entry.desc,
            node_tags: entry.tags,
            connected_node_title: "",
            connected_node_id: "",
            connected_node_desc: "",
            connected_node_tags: [],
            row_data_type: SheetDataTypeKind.Node
        });

        const entry_relationships = await getAccountRelationships(entry.id)
        //console.log(entry_relationships)
        for (const relationship of entry_relationships.outgoing) {
            //console.log(relationship)
            const connectedEntry = await getAccountEntry(relationship.toId);
            //console.log(targetEntry)
            result.push({
                key: entry.title + connectedEntry.id + SheetDataTypeKind.Linked,
                id: connectedEntry.id,
                node_id: entry.id,
                node_title: entry.title,
                node_desc: entry.desc,
                node_tags: entry.tags,
                connected_node_id: connectedEntry.id,
                connected_node_title: connectedEntry.title,
                connected_node_desc: connectedEntry.desc,
                connected_node_tags: connectedEntry.tags,
                row_data_type: SheetDataTypeKind.Linked
            });
        }
    }

    return result;
}

export async function explorerAccountEntryStartLeaf(startId: string) {
    return http<AccountEntryTree>(`http://127.0.0.1:8000/v1/account-entries/${startId}/explore-start-leaf`);
}

export async function explorerAllAccountEntryStartLeaf() {
    const accountEntries = await getAccountEntries()
    console.log(accountEntries)
    const allStartLeaf = [];
    for(const accountEntry of accountEntries) {
        allStartLeaf.push(await explorerAccountEntryStartLeaf(accountEntry.id));
    }
    return allStartLeaf;
}

export async function explorerAccountEntryStartLeafReverse(startId: string) {
    return http<AccountEntryTree>(`http://127.0.0.1:8000/v1/account-entries/${startId}/explore-start-leaf-reverse`);
}

export async function explorerAllAccountEntryStartLeafReverse() {
    const accountEntries = await getAccountEntries()
    console.log(accountEntries)
    const allStartLeaf = [];
    for(const accountEntry of accountEntries) {
        allStartLeaf.push(await explorerAccountEntryStartLeafReverse(accountEntry.id));
    }
    return allStartLeaf;
}

