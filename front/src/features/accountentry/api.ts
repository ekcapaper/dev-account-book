import { http } from "../../lib/fetch";


export type AccountEntry = { id: string; title: string; desc:string; tags: string[] };


export const getAccountEntry = () =>{
    const params = new URLSearchParams({
        limit: "50",
        offset: "0",
    });
    return http<AccountEntry[]>(`http://127.0.0.1:8000/v1/account-entries?${params}`);
}