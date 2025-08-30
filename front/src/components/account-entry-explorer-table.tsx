import React from 'react';
import type {TableColumnsType} from 'antd';
import {Table} from 'antd';
import {useExplorerAccountEntryTreeQuery} from "../hooks/use-account-entry-query.ts";
import type {AccountEntryTree} from "../types/account-entry.ts";

interface DataType {
    key: React.ReactNode;
    id: string;
    title: string;
    desc: string | null;
    tags: string[];
    children?: DataType[];
}

function mapApiToDataType(apiData: AccountEntryTrees): DataType {
    return {
        key: apiData.id,             // ReactNode → string도 가능
        name: apiData.title,         // title → name
        age: 0,                      // age 없음 → 더미 값 or 제거 필요
        address: apiData.desc ?? "", // desc → address
        children: apiData.children?.map(mapApiToDataType),
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

    const convert_data = map()

    console.log(data)

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