// AccountEntryExplorerNestedTable.tsx
import React from 'react';
import type { TableColumnsType } from 'antd';
import { Table } from 'antd';

import {
    useExplorerAccountEntryTreeQuery,
} from '../hooks/use-account-entry-query.ts';
import type { AccountEntryTree } from '../types/account-entry.ts';


interface InnerDataType{
    key: React.Key;
    depth: number;
    id: string;
    title: string;
    desc: string | null;
    tags: string[];
}

interface DataType{
    key: React.Key;
    id: string;
    title: string;
    desc: string | null;
    tags: string[];
    children?: InnerDataType[];
}

function toInnerDataType(node:AccountEntryTree, depth:number = 0, result:InnerDataType[] = [], visitSet:Set<string> = new Set()):InnerDataType[]{
    if(visitSet.has(node.id)){
        return result;
    }
    visitSet.add(node.id);

    if(node.children){
        for (const child of node.children) {
            result.push(
                {
                    key: node.id + child.id + depth,
                    depth: depth,
                    id: child.id,
                    title: child.title,
                    desc: child.desc,
                    tags: child.tags,
                }
            )
            const result_inner = toInnerDataType(child, depth+1);
            result.push(...result_inner);
        }
    }
    return result;
}

// AccountEntryTree -> DataType로 변환 (재귀)
function toDataType(node: AccountEntryTree): DataType {
    return {
        ...node,
        key: `${node.id}`,
        children: toInnerDataType(
            node
        )
    };
}

// 컬럼 정의 (원하는 대로 수정 가능)
const columns: TableColumnsType<DataType> = [
    { title: 'Title', dataIndex: 'title', key: 'title' },
    { title: 'Description', dataIndex: 'desc', key: 'desc' },
];

// 하위(확장) 테이블도 다시 중첩 테이블 형태로 렌더 (재귀)
const expandedRowRender = (record: DataType) => {
    if (!record.children || record.children.length === 0) return null;

    return (
        <Table<DataType>
            columns={columns}
            dataSource={record.children}
            rowKey="key"
            pagination={false}
            // 트리 모드 비활성화 (children을 트리로 쓰지 않도록)
            childrenColumnName="__children"
            expandable={{
                expandedRowRender,
                rowExpandable: (r) => !!(r.children && r.children.length),
                defaultExpandAllRows: true, // ✅ 내부 테이블도 기본 전체 펼침
            }}
        />
    );
};

const AccountEntryExplorerNestedTable: React.FC = () => {
    const { data, isLoading, error } = useExplorerAccountEntryTreeQuery();

    if (isLoading) return <p>Loading...</p>;
    if (error) return <p>{(error as Error).message}</p>;
    if (!data) return null;

    const dataSource = data.map(toDataType);

    return (
        <>
            <Table<DataType>
                columns={columns}
                dataSource={dataSource}
                rowKey="key"
                // 트리 모드 비활성화 (children을 트리로 쓰지 않도록)
                childrenColumnName="__children"
                expandable={{
                    expandedRowRender,
                    rowExpandable: (record) => !!(record.children && record.children.length),
                    defaultExpandAllRows: true, // ✅ 바깥 테이블도 기본 전체 펼침
                }}
            />
        </>
    );
};

export default AccountEntryExplorerNestedTable;
