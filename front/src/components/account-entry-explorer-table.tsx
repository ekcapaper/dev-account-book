import React from 'react';
import type {TableColumnsType} from 'antd';
import {Table} from 'antd';
import {useExplorerAccountEntryTreeQuery} from "../hooks/use-account-entry-query.ts";
import type {AccountEntryTree} from "../types/account-entry.ts";

export interface DataType extends AccountEntryTree {
    key: React.ReactNode;
}

function mapToDataType(node: AccountEntryTree): DataType {
    return {
        ...node,
        key: node.id, // 보통 key는 id로 대체
        children: node.children?.map(mapToDataType),
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

    const convert_data = mapToDataType(data)

    console.log(convert_data)

    return (
        <>
            <Table<DataType>
                columns={columns}
                dataSource={[convert_data]}
                expandable={{
                    defaultExpandAllRows: true,   // ← 여기로 이동
                }}
            />
        </>
    );
};

export default AccountEntryExplorerTable;