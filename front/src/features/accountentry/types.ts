export enum DataTypeKind {
    Node = 'node',
    Linked = 'linked',
}

export type AccountEntryTree = {
    id: string;
    title: string;
    desc:string;
    tags: string[];
    relates_to: AccountEntryTree[];
};
