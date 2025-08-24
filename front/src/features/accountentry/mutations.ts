// features/account/mutations.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { accountEntryKeys } from "./keys";
import {type AccountEntry, createAccountEntry} from "./api.ts";

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
