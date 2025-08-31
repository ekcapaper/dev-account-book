import React from 'react';
import type { TableColumnsType } from 'antd';
import { Table } from 'antd';

import {
    useExplorerAccountEntryTreeQuery,
} from "../hooks/use-account-entry-query.ts";
import type { AccountEntryTree } from "../types/account-entry.ts";

interface DataType{
    key: React.Key;
    id: string;
    title: string;
    desc: string | null;
    tags: string[];
    children?: DataType[];
}

function mapToDataType(node: AccountEntryTree, depth: number = 0): DataType {
    return {
        ...node,
        key: `${node.id}${depth}`,
        children: (node.children || []).map((child) => mapToDataType(child, depth + 1)),
    };
}

const columns: TableColumnsType<DataType> = [
    { title: 'Title', dataIndex: 'title', key: 'title' },
    { title: 'Description', dataIndex: 'desc', key: 'desc' }
];

// Recursively render nested tables for children, similar to AntD demo's expandedRowRender
const expandedRowRender = (record: DataType) => {
    if (!record.children || record.children.length === 0) return null;
    return (
        <Table<DataType>
            columns={columns}
            dataSource={record.children}
            rowKey="key"
            pagination={false}
            expandable={{
                expandedRowRender,
                rowExpandable: (r) => !!(r.children && r.children.length),
            }}
        />
    );
};

const AccountEntryExplorerNestedTable: React.FC = () => {
    const { data, isLoading, error } = useExplorerAccountEntryTreeQuery();

    if (isLoading) return <p>Loading...</p>;
    if (error) return <p>{(error as Error).message}</p>;
    if (!data) return null;

    const dataSource = data.map(mapToDataType);
    // Match the demo behavior: expand only the first row by default
    const defaultExpandedRowKeys = dataSource[0] ? [String(dataSource[0].key)] : [];

    return (
        <>
            <Table<DataType>
                columns={columns}
                dataSource={dataSource}
                rowKey="key"
                expandable={{
                    expandedRowRender,
                    rowExpandable: (record) => !!(record.children && record.children.length),
                    defaultExpandedRowKeys,
                }}
            />
        </>
    );
};

export default AccountEntryExplorerNestedTable;
