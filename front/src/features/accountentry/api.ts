import {http} from "../../lib/fetch";
import type {AccountEntry, RelationList, RelationResponseDTO} from "./types.ts";


export const getAccountEntries = () => {
    const params = new URLSearchParams({
        limit: "50",
        offset: "0",
    });
    return http<AccountEntry[]>(`http://127.0.0.1:8000/v1/account-entries?${params}`);
}

export const getAccountEntry = (id: string) => {
    return http<AccountEntry>(`http://127.0.0.1:8000/v1/account-entries/${id}`);
}

export const getAccountRelationships = (id: string) => {
    return http<RelationList>(`http://127.0.0.1:8000/v1/account-entries/${id}/relations`);
}

export async function createAccountEntry(body: Omit<AccountEntry, "id">) {
    const res = await fetch(`http://127.0.0.1:8000/v1/account-entries`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
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
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

export async function createAccountEntryRelationshipApi(from_id: string, to_id: string): Promise<RelationResponseDTO> {
    const res = await fetch(`http://127.0.0.1:8000/v1/account-entries/${from_id}/relations`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            "to_id": `${to_id}`,
            "kind": "RELATES_TO",
        }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json()
}

export async function deleteAccountEntryRelationshipApi(from_id: string, to_id: string) {
    const res = await fetch(`http://127.0.0.1:8000/v1/account-entries/${from_id}/relations/RELATES_TO/${to_id}`, {
        method: "DELETE",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    try {
        return await res.json();
    } catch {
        return null;
    }
}

