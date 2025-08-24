// features/account/mutations.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { accountEntryKeys } from "./keys";
import {type AccountEntry, createAccountEntry, deleteAccountEntry} from "./api.ts";

export function useCreateAccountEntry() {
    const qc = useQueryClient();

    return useMutation({
        mutationFn: (body: Omit<AccountEntry, "id">) =>
            createAccountEntry(body),

        onSuccess: () => {
            // 새로 생성된 뒤 목록을 갱신하기 위해 invalidate
            qc.invalidateQueries({ queryKey: accountEntryKeys.all });
        },
    });
}

export function useDeleteAccountEntry() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (id: string) => deleteAccountEntry(id),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: accountEntryKeys.all }); // 목록 갱신
        },
    });
}

export function useUpdateAccountEntry(limit = 50, offset = 0) {
    const qc = useQueryClient();

    return useMutation({
        mutationFn: ({ id, body }: { id: string; body: Partial<Omit<AccountEntry, "id">> }) =>
            updateAccountEntry(id, body),

        onSuccess: (_data, { id }) => {
            // 1) 목록 무효화 → 자동 새로고침
            qc.invalidateQueries({ queryKey: accountKeys.list(limit, offset) });
            // 2) 단건 쿼리 캐시도 쓰고 있다면 같이 갱신
            qc.invalidateQueries({ queryKey: ["account-entry", id] });
        },
    });
}