import React from 'react';
import type {TableColumnsType} from 'antd';
import {Table} from 'antd';
import {accountEntryKeys} from "../hooks/query-keys.ts";
import {useQuery} from "@tanstack/react-query";
import {explorerAccountEntryStartLeaf} from "../services/account-entry-api-facade.ts";

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
    const {data: data2, isLoading, error} = useQuery({
        queryKey: accountEntryKeys.tree_all,     // 캐싱 키
        queryFn: explorerAccountEntryStartLeaf,     // 실제 호출 함수
    });

    if (isLoading) {
        return <p>Loading...</p>;
    }
    if (error) {
        return <p>{error.message}</p>;
    }

    console.log(data2);

    return (
        <>
            <Table<DataType>
                columns={columns}
                dataSource={[data2]}
                expandable={{
                    defaultExpandAllRows: true,   // ← 여기로 이동
                }}
            />
        </>
    );
};

export default AccountEntryExplorerTable;