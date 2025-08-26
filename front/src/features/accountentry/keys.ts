export const accountEntryKeys = {
    all: ["accountEntrys"] as const,
    full_all: ["accountEntryAndRelationships"] as const,
    tree_key: (id: string) => ['tree', id] as const,
};