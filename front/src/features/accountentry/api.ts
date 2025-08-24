import { http } from "../../lib/fetch";


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
    return await getAccountEntries();
}
