// 행 타입 단일화
import React from "react";
import {SheetDataTypeKind} from "../constants/sheet-data-type-kind.ts";

export interface AccountEntryTableDataType {
    key: React.Key;
    id: string;
    node_id: string;
    node_title: string;
    node_desc: string;
    node_tags: Array<string>;
    connected_node_id: string;
    connected_node_title: string;
    connected_node_desc: string;
    connected_node_tags: Array<string>;
    row_data_type: SheetDataTypeKind;
    operation?: React.ReactNode;
}