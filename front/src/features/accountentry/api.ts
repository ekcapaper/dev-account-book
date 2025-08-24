import { http } from "../../lib/fetch";
import {DataTypeKind} from "./types.ts";


export type AccountEntry = { id: string; title: string; desc:string; tags: string[] };
export type AccountRelationship = { from_id : string; to_id : string; kind: string; props: object };
export type AccountEntryRelationship = {outgoing: AccountRelationship[]; incoming: AccountRelationship[] };

export const getAccountEntries = () =>{
    const params = new URLSearchParams({
        limit: "50",
        offset: "0",
    });
    return http<AccountEntry[]>(`http://127.0.0.1:8000/v1/account-entries?${params}`);
}

export const getAccountEntry = (id: string) =>{
    return http<AccountEntry>(`http://127.0.0.1:8000/v1/account-entries/${id}`);
}

export const getAccountRelationships = (id: string) => {
    return http<AccountEntryRelationship>(`http://127.0.0.1:8000/v1/account-entries/${id}/relations`);
}

export const getConvertedFullAccountEntriesAndRelationships = async () =>{
    const result = []
    const data = await getAccountEntries();
    for (const entry of data){
        //console.log(entry)
        result.push({
            key: entry.id,
            id: entry.id,
            node_title: entry.title,
            connected_node_title: "",
            row_data_type: DataTypeKind.Node
        });

        const entry_relationships = await getAccountRelationships(entry.id)
        //console.log(entry_relationships)
        for (const relationship of entry_relationships.outgoing){
            //console.log(relationship)
            const connectedEntry = await getAccountEntry(relationship.to_id);
            //console.log(targetEntry)
            result.push({
                key: connectedEntry.id + DataTypeKind.Linked,
                id: connectedEntry.id,
                node_title: "",
                connected_node_title: connectedEntry.title,
                row_data_type: DataTypeKind.Linked
            });
        }
    }

    return result;
}

export async function createAccountEntry(body: Omit<AccountEntry, "id">) {
    const res = await fetch(`http://127.0.0.1:8000/v1/account-entries`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json() as Promise<AccountEntry>;
}

export async function deleteAccountEntry(id: string) {
    const res = await fetch(`http://127.0.0.1:8000/v1/account-entries/${id}`, {
        method: "DELETE",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    try {
        return await res.json();
    } catch {
        return null;
    }
}

export async function updateAccountEntry(
    accountEntryId: string,
    body: Partial<Omit<AccountEntry, "id">> // 일부 필드만 수정 가능
): Promise<AccountEntry> {
    const res = await fetch(`http://127.0.0.1:8000/v1/account-entries/${accountEntryId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

export async function createAccountEntryRelationship(from_id:string , to_id: string) {
    const res = await fetch(`http://127.0.0.1:8000/v1/account-entries/${from_id}/relations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            "to_id": `${to_id}`,
            "kind": "RELATES_TO",
        }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json() as Promise<AccountEntry>;
}
