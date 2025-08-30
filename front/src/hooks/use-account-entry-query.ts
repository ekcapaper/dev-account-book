import {
    explorerAllAccountEntryStartLeaf,
    explorerAllAccountEntryStartLeafReverse
} from "../services/account-entry-api-facade.ts";
import {useQuery} from "@tanstack/react-query";
import {accountEntryKeys} from "./query-keys.ts";


export function useExplorerAccountEntryTreeQuery() {
    return useQuery({
        queryKey: accountEntryKeys.tree_all,     // 캐싱 키
        queryFn: explorerAllAccountEntryStartLeaf,     // 실제 호출 함수
    });
}

export function useExplorerAccountEntryTreeQueryReverse() {
    return useQuery({
        queryKey: accountEntryKeys.tree_all_reverse,     // 캐싱 키
        queryFn: explorerAllAccountEntryStartLeafReverse,     // 실제 호출 함수
    });
}
