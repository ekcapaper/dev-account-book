import React, { useState } from 'react';
import { Space, Switch, Table } from 'antd';
import type { TableColumnsType, TableProps } from 'antd';
import {accountEntryKeys} from "../features/accountentry/keys.ts";
import {useQuery} from "@tanstack/react-query";
import {explorerAccountEntryStartLeaf} from "../features/accountentry/api.ts";
import {http} from "../lib/fetch.ts";
import type {AccountEntryTree} from "../features/accountentry/types.ts";

type TableRowSelection<T extends object = object> = TableProps<T>['rowSelection'];

interface DataType {
    key: React.ReactNode;
    name: string;
    age: number;
    address: string;
    children?: DataType[];
}

const columns: TableColumnsType<DataType> = [
    {
        title: 'Name',
        dataIndex: 'name',
        key: 'name',
    },
    {
        title: 'Age',
        dataIndex: 'age',
        key: 'age',
        width: '12%',
    },
    {
        title: 'Address',
        dataIndex: 'address',
        width: '30%',
        key: 'address',
    },
];

const data: DataType[] = [
    {
        key: 1,
        name: 'John Brown sr.',
        age: 60,
        address: 'New York No. 1 Lake Park',
        children: [
            {
                key: 11,
                name: 'John Brown',
                age: 42,
                address: 'New York No. 2 Lake Park',
            },
            {
                key: 12,
                name: 'John Brown jr.',
                age: 30,
                address: 'New York No. 3 Lake Park',
                children: [
                    {
                        key: 121,
                        name: 'Jimmy Brown',
                        age: 16,
                        address: 'New York No. 3 Lake Park',
                    },
                ],
            },
            {
                key: 13,
                name: 'Jim Green sr.',
                age: 72,
                address: 'London No. 1 Lake Park',
                children: [
                    {
                        key: 131,
                        name: 'Jim Green',
                        age: 42,
                        address: 'London No. 2 Lake Park',
                        children: [
                            {
                                key: 1311,
                                name: 'Jim Green jr.',
                                age: 25,
                                address: 'London No. 3 Lake Park',
                            },
                            {
                                key: 1312,
                                name: 'Jimmy Green sr.',
                                age: 18,
                                address: 'London No. 4 Lake Park',
                            },
                        ],
                    },
                ],
            },
        ],
    },
    {
        key: 2,
        name: 'Joe Black',
        age: 32,
        address: 'Sydney No. 1 Lake Park',
        children: [
            {
                key: 1311,
                name: 'Jim Green jr.',
                age: 25,
                address: 'London No. 3 Lake Park',
            }]
    },
];

// rowSelection objects indicates the need for row selection
const rowSelection: TableRowSelection<DataType> = {
    onChange: (selectedRowKeys, selectedRows) => {
        console.log(`selectedRowKeys: ${selectedRowKeys}`, 'selectedRows: ', selectedRows);
    },
    onSelect: (record, selected, selectedRows) => {
        console.log(record, selected, selectedRows);
    },
    onSelectAll: (selected, selectedRows, changeRows) => {
        console.log(selected, selectedRows, changeRows);
    },
};


function normalizeToChildren(obj: any): any {
    if (Array.isArray(obj)) {
        return obj.map(normalizeToChildren)
    } else if (obj && typeof obj === "object") {
        const result: any = {}
        for (const [key, value] of Object.entries(obj)) {
            if (Array.isArray(value) && value.every(v => typeof v === "object" && v !== null)) {
                // 이 키가 자식 노드 배열이면 전부 children으로 병합
                result.children = (result.children ?? []).concat(normalizeToChildren(value))
            } else {
                result[key] = normalizeToChildren(value)
            }
        }
        return result
    }
    return obj
}


const TechExplorerTable: React.FC = () => {
    const [checkStrictly, setCheckStrictly] = useState(false);

    const { data:data2, isLoading, error } = useQuery({
        queryKey: accountEntryKeys.tree_all,     // 캐싱 키
        queryFn: explorerAccountEntryStartLeaf,     // 실제 호출 함수
    });

    if(isLoading){
        return <p>Loading...</p>;
    }
    if(error){
        return <p>{error.message}</p>;
    }
    
    console.log(data2);

    return (
        <>
            <Table<DataType>
                columns={columns}
                dataSource={data}
            />
        </>
    );
};

export default TechExplorerTable;