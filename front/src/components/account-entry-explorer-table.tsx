import React from 'react';
import type {TableColumnsType} from 'antd';
import {Table} from 'antd';
import {useExplorerAccountEntryTreeQuery} from "../hooks/use-account-entry-query.ts";

interface DataType {
    key: React.ReactNode;
    name: string;
    age: number;
    address: string;
    children?: DataType[];
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
    },
    {
        title: 'tags',
        dataIndex: 'tags',
        key: 'tags',
    }
];


const AccountEntryExplorerTable: React.FC = () => {
    const {data, isLoading, error} = useExplorerAccountEntryTreeQuery()

    if (isLoading) {
        return <p>Loading...</p>;
    }
    if (error) {
        return <p>{error.message}</p>;
    }

    return (
        <>
            <Table<DataType>
                columns={columns}
                dataSource={[data]}
                expandable={{
                    defaultExpandAllRows: true,   // ← 여기로 이동
                }}
            />
        </>
    );
};

export default AccountEntryExplorerTable;