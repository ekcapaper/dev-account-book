// AccountEntryExplorerNestedTable.tsx
import React from 'react';
import type { TableColumnsType } from 'antd';
import { Table } from 'antd';

import {
    useExplorerAccountEntryTreeQuery,
} from '../hooks/use-account-entry-query.ts';
import type { AccountEntryTree } from '../types/account-entry.ts';

export interface DataType extends AccountEntryTree {
    key: React.Key;
    children?: DataType[];
}

// AccountEntryTree -> DataType로 변환 (재귀)
function toDataType(node: AccountEntryTree, depth = ''): DataType {
    return {
        ...node,
        key: `${node.id}${depth}`,
        children: (node.children ?? []).map((child) =>
            toDataType(child, `${depth}-${node.id}`)
        ),
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

    // 상위 테이블에는 '루트' 노드만 올리기 (중복 노출 방지)
    // data에 자식 노드가 루트에도 중복 포함되어 있으면 바깥/안쪽에 둘 다 보이는 문제가 생김
    const collectChildIds = (nodes: AccountEntryTree[], out = new Set<string>()) => {
        nodes.forEach((n) => {
            (n.children ?? []).forEach((c) => {
                out.add(String(c.id));
                collectChildIds([c], out);
            });
        });
        return out;
    };
    const childIds = collectChildIds(data);
    const rootsOnly = data.filter((n) => !childIds.has(String(n.id)));

    const dataSource = rootsOnly.map(toDataType);

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
