// features/account/mutations.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { accountEntryKeys } from "./keys";
import {
    type AccountEntry,
    createAccountEntry,
    createAccountEntryRelationship,
    deleteAccountEntry,
    updateAccountEntry
} from "./api.ts";

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

export function useUpdateAccountEntry() {
    const qc = useQueryClient();

    return useMutation({
        mutationFn: ({ id, body }: { id: string; body: Partial<Omit<AccountEntry, "id">> }) =>
            updateAccountEntry(id, body),

        onSuccess: (_data, { id }) => {
            qc.invalidateQueries({ queryKey: accountEntryKeys.all });
        },
    });
}

type Vars = { from_id: string; to_id: string };
export function useCreateAccountEntryRelationship() {
    const qc = useQueryClient();
    
    return useMutation({
        mutationFn: ({from_id, to_id}:Vars) =>
            createAccountEntryRelationship(from_id, to_id),

        onSuccess: () => {
            // 새로 생성된 뒤 목록을 갱신하기 위해 invalidate
            qc.invalidateQueries({ queryKey: accountEntryKeys.all });
        },
    });
}
