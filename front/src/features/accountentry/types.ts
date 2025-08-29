// src/api/dto/accountEntry.ts

export type RelKind =
    | "RELATES_TO"
    | "INFLUENCES"
    | "BLOCKS"
    | "DUPLICATES";

export type AccountEntryCreateRequestDTO = {
    title: string;
    desc?: string | null;
    tags?: string[]; // 서버 기본값 [] 지원
};

export type AccountEntryPatchRequestDTO = {
    title?: string | null;
    desc?: string | null;
    tags?: string[] | null;
};

export type AccountEntryResponseDTO = {
    id: string;
    title: string;
    desc: string | null;
    tags: string[];
};

export type RelationPropsDTO = {
    note?: string | null;
    createdAt?: string; // ISO datetime string
    updatedAt?: string; // ISO datetime string
    // 백엔드가 extra='allow' 이므로 임의 키 허용
    [key: string]: unknown;
};

export type RelationCreateRequestDTO = {
    to_id: string;
    kind: RelKind;
    props?: RelationPropsDTO;
};

export type RelationResponseDTO = {
    from_id: string;
    to_id: string;
    kind: RelKind;
    props: RelationPropsDTO; // 항상 객체(빈 객체 가능)
};

export type RelationListResponseDTO = {
    outgoing: RelationResponseDTO[];
    incoming: RelationResponseDTO[];
};

export type CountResponseDTO = {
    total: number;
};
