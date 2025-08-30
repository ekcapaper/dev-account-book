// ===========================
// API DTO (백엔드 wire 형식)
// ===========================

// RelKind (백엔드 enum과 동일)
export type RelKind =
    | "RELATES_TO"
    | "INFLUENCES"
    | "BLOCKS"
    | "DUPLICATES";

// AccountEntry
export type AccountEntryCreateRequestDTO = {
    title: string;
    desc?: string | null;
    tags?: string[]; // 서버 기본값 []
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

// Relations
export type RelationPropsDTO = {
    note?: string | null;
    createdAt?: string; // ISO datetime string
    updatedAt?: string; // ISO datetime string
    // extra='allow' 대응: 임의 키 허용
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
    props: RelationPropsDTO; // 빈 객체일 수 있음
};

export type RelationListResponseDTO = {
    outgoing: RelationResponseDTO[];
    incoming: RelationResponseDTO[];
};

// Count
export type CountResponseDTO = {
    total: number;
};

// 목록 응답 모양이 확정이 아니면 둘 다 대비
export type AccountEntryListResponseDTO =
    | { items: AccountEntryResponseDTO[] } // (예: { items: [...] })
    | AccountEntryResponseDTO[];           // (예: 그냥 배열)

// ==================================
// (선택) 프론트 도메인 모델 (내부용)
// ==================================

export type RelationProps = {
    note?: string | null;
    createdAt?: Date;
    updatedAt?: Date;
    [key: string]: unknown;
};

export type Relation = {
    fromId: string;
    toId: string;
    kind: RelKind;
    props: RelationProps;
};

export type RelationList = {
    outgoing: Relation[];
    incoming: Relation[];
};

export type AccountEntry = {
    id: string;
    title: string;
    desc?: string | null;
    tags: string[];
};

export type AccountEntryTree = {
    id: string;
    title: string;
    desc: string | null;
    tags: string[];
    children: AccountEntryTree[];
};