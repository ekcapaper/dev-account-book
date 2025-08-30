import React from 'react';
import type {TableColumnsType} from 'antd';
import {Table} from 'antd';
import {useExplorerAccountEntryTreeQuery} from "../hooks/use-account-entry-query.ts";
import type {AccountEntryTree} from "../types/account-entry.ts";

export interface DataType extends AccountEntryTree {
    key: React.ReactNode;
}

function mapToDataType(node: AccountEntryTree, depth: string = ""): DataType {
    return {
        ...node,
        key: node.id + depth,
        children: node.children.map((child)=> mapToDataType(child, depth + "-" + node.id)),
    };
}

const columns: TableColumnsType<DataType> = [
    {
        title: 'title',
        dataIndex: 'title',
        key: 'title',
    },
    {
        title: 'desc',
        dataIndex: 'desc',
        key: 'desc'
    }];


const AccountEntryExplorerTable: React.FC = () => {
    const {data, isLoading, error} = useExplorerAccountEntryTreeQuery()

    if (isLoading) {
        return <p>Loading...</p>;
    }
    if (error) {
        return <p>{error.message}</p>;
    }
    if (!data) return null;
    //console.log(data)
    const convert_data = data.map((dataOne) => mapToDataType(dataOne));
    //console.log(convert_data)

    return (
        <>
            <Table<DataType>
                columns={columns}
                dataSource={convert_data}
                expandable={{
                    defaultExpandAllRows: true,   // ← 여기로 이동
                    
                }}
            />
        </>
    );
};

export default AccountEntryExplorerTable;