import React, {useContext, useEffect, useState} from 'react';
import {Button, Form, type GetRef, Input, Popconfirm, Space, Table, type TableProps} from 'antd';
import {useQuery} from "@tanstack/react-query";
import {accountEntryKeys} from "../hooks/query-keys.ts";
import {
    useCreateAccountEntry,
    useCreateAccountEntryRelationship,
    useDeleteAccountEntry,
    useDeleteAccountEntryRelationship,
    useUpdateAccountEntry
} from "../hooks/use-account-entry-mutations.ts";
import {SheetDataTypeKind} from "../constants/sheet-data-type-kind.ts";
import {getConvertedFullAccountEntriesAndRelationships} from "../services/account-entry-api-facade.ts";

type FormInstance<T> = GetRef<typeof Form<T>>;

// 행 타입 단일화
interface DataType {
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

const EditableContext = React.createContext<FormInstance<DataType> | null>(null);

// Editable Row
interface EditableRowProps {
    index: number;
}

const EditableRow: React.FC<EditableRowProps> = ({index, ...props}) => {
    const [form] = Form.useForm<DataType>();
    return (
        <Form form={form} component={false}>
            <EditableContext.Provider value={form}>
                <tr {...props} />
            </EditableContext.Provider>
        </Form>
    );
};

// Editable Cell
interface EditableCellProps {
    title: React.ReactNode;
    editable: boolean;
    dataIndex: keyof DataType;
    record: DataType;
    handleSave: (record: DataType) => void;
}

const EditableCell: React.FC<React.PropsWithChildren<EditableCellProps>> = ({
                                                                                title,
                                                                                editable,
                                                                                children,
                                                                                dataIndex,
                                                                                record,
                                                                                handleSave,
                                                                                ...restProps
                                                                            }) => {
    const form = useContext(EditableContext)!;

    useEffect(() => {
        if (editable) {
            form.setFieldsValue({[dataIndex]: record[dataIndex]});
        }
    }, [form, dataIndex, record, editable]);

    const save = async () => {


        try {
            const values = await form.validateFields();
            handleSave({...record, ...values});
        } catch (errInfo) {
            console.log('Save failed:', errInfo);
        }
    };

    let childNode = children;

    if (dataIndex == "node_title" && (record.row_data_type === SheetDataTypeKind.Linked)) {
        return <td style={{ padding: 0, margin: 0 }}></td>;
    }

    if (dataIndex == "connected_node_title" && (record.row_data_type === SheetDataTypeKind.Node)) {
        return <td style={{ padding: 0, margin: 0 }}></td>;
    }

    if (editable) {
        childNode = (
            <Form.Item
                style={{margin: 0, padding: 0}}
                name={dataIndex as string}
                rules={[{required: false, message: `${title} is required.`}]}
            >
                <Input.TextArea
                    id={`${record.key}_${String(dataIndex)}`}
                    onPressEnter={(e) => {
                        e.preventDefault(); // 줄바꿈 방지
                        save();
                    }}
                    onBlur={save}
                    autoSize={{minRows: 1, maxRows: 6}}
                    style={{
                        width: '100%',
                        margin: 0,
                        padding: 0,
                        border: 'none',
                        borderRadius: 0,
                        boxShadow: 'none',
                        minHeight: '100%',
                        background: 'transparent',
                        resize: 'none',
                    }}
                />
            </Form.Item>
        );
    }
    return <td {...restProps} style={{ padding: 0, margin: 0 }}>{childNode}</td>;
};

type ColumnTypes = Exclude<TableProps<DataType>['columns'], undefined>;

const AccountEntrySheet: React.FC = () => {
    const [dataSource, setDataSource] = useState<DataType[]>([]);
    const [connectedNodeTitleValue, setConnectedNodeTitleValue] = useState<string>();

    // AccountEntry CRUD
    const {data, isLoading, error} = useQuery({
        queryKey: accountEntryKeys.all,     // 캐싱 키
        queryFn: getConvertedFullAccountEntriesAndRelationships,     // 실제 호출 함수
    });
    const createAccountEntry = useCreateAccountEntry();
    const deleteAccountEntry = useDeleteAccountEntry();
    const patchAccountEntry = useUpdateAccountEntry();

    // AccountEntry Relationship
    const createAccountEntryRelationship = useCreateAccountEntryRelationship();
    const deleteAccountEntryRelationship = useDeleteAccountEntryRelationship();

    useEffect(() => {
        if (data) {
            setDataSource(data)
        }
    }, [data]);

    console.log(data)

    if (isLoading) return <p>로딩중...</p>;
    if (error) return <p>에러 발생!</p>;


    // handler
    const handleDelete = (id: string) => {
        deleteAccountEntry.mutate(id);
    };

    const handleLinkDelete = (from_id: string, to_id: string) => {
        console.log(from_id, to_id);
        deleteAccountEntryRelationship.mutate({from_id, to_id});
    }

    // 특정 행(record) 아래에 연결 노드 추가
    const handleAddConnectedNode = (record: DataType) => {
        if (!data) return;
        for (const nodeData of data) {
            //console.log(nodeData);
            if (nodeData.node_title == connectedNodeTitleValue) {
                createAccountEntryRelationship.mutate({
                    from_id: record.id,
                    to_id: nodeData.id
                })
            }
        }
    };


    const handleAdd = () => {
        createAccountEntry.mutate({
            title: "New",
            desc: "",
            tags: ["TAG"]
        })
    };

    const handleSave = (row: DataType) => {
        setDataSource((prev) => {
            //console.log("values");
            //console.log(row)

            if (row.row_data_type == SheetDataTypeKind.Node) {
                patchAccountEntry.mutate({
                    "id": row.id,
                    "body": {
                        "title": row.node_title,
                        "desc": row.node_desc,
                    }
                })
            } else if (row.row_data_type === SheetDataTypeKind.Linked) {
                patchAccountEntry.mutate({
                    "id": row.id,
                    "body": {
                        "title": row.connected_node_title,
                        "desc": row.connected_node_desc,
                    }
                })
            }

            const idx = prev.findIndex((item) => item.key === row.key);
            if (idx === -1) return prev;
            const next = prev.slice();
            next.splice(idx, 1, {...prev[idx], ...row});
            return next;
        });
    };


    const defaultColumns: (ColumnTypes[number] & {
        editable?: boolean;
        dataIndex: keyof DataType;
    })[] = [
        {
            title: 'node_title',
            dataIndex: 'node_title',
            width: '10%',
            editable: true,
            onCell: (record: DataType) => ({
                record,
                editable: record.row_data_type === SheetDataTypeKind.Node, // 행 조건에 따른 편집 여부
                dataIndex: 'node_title',
                title: 'node_title',
                handleSave, // 상위의 저장 핸들러
            }),
        },
        {
            title: 'node_desc',
            dataIndex: 'node_desc',
            width: '10%',
            editable: true,
            onCell: (record: DataType) => ({
                record,
                editable: record.row_data_type === SheetDataTypeKind.Node, // 행 조건에 따른 편집 여부
                dataIndex: 'node_desc',
                title: 'node_desc',
                handleSave, // 상위의 저장 핸들러
            }),
        },
        {
            title: 'connected_node_title',
            dataIndex: 'connected_node_title',
            width: '10%',
            editable: true,
            onCell: (record: DataType) => ({
                record,
                editable: record.row_data_type === SheetDataTypeKind.Linked,
                dataIndex: 'connected_node_title',
                title: 'connected_node_title',
                handleSave,
            }),
        },
        {
            title: 'connected_node_desc',
            dataIndex: 'connected_node_desc',
            width: '10%',
            editable: true,
            onCell: (record: DataType) => ({
                record,
                editable: record.row_data_type === SheetDataTypeKind.Linked,
                dataIndex: 'connected_node_desc',
                title: 'connected_node_desc',
                handleSave,
            }),
        },

        {
            title: 'row_data_type',
            dataIndex: 'row_data_type',
            width: '10%',
            editable: false,
            onCell: (record: DataType) => ({
                record,
                editable: false,
                dataIndex: 'row_data_type',
                title: 'row_data_type',
                handleSave,
            }),
        },
        {
            title: 'operation',
            dataIndex: 'operation',
            width: '25%',
            onCell: (record: DataType) => ({
                record,
                editable: false,
                dataIndex: 'operation',
                title: 'operation',
                handleSave,
            }),
            render: (_, record) => (
                <div>
                    {(() => {
                        if (record.row_data_type === SheetDataTypeKind.Node) {
                            return (
                                <Space split="|">
                                    <Popconfirm title="Sure to delete?" onConfirm={() => handleDelete(record.id)}>
                                        <a>항목 삭제</a>
                                    </Popconfirm>
                                    <div>
                                        <Space>
                                            <Input value={connectedNodeTitleValue}
                                                   onChange={(e) => setConnectedNodeTitleValue(e.target.value)}></Input>
                                            <a onClick={() => handleAddConnectedNode(record)}>
                                                연결된 항목 추가
                                            </a>
                                        </Space>
                                    </div>
                                </Space>
                            );
                        }
                        else if (record.row_data_type === SheetDataTypeKind.Linked) {
                            return (
                                <Space split="|">
                                    <Popconfirm title="Sure to delete?"
                                                onConfirm={() => handleLinkDelete(record.node_id, record.connected_node_id)}>
                                        <a>링크 삭제</a>
                                    </Popconfirm>
                                </Space>
                            );
                        }
                        return null;
                    })()}

                </div>
            ),
        },
    ];

    const components = {
        body: {
            row: EditableRow,
            cell: EditableCell,
        },
    };

    return (
        <div>
            <Button onClick={handleAdd} type="dashed" style={{marginBottom: 16}}>
                노드 항목 추가
            </Button>
            <Table<DataType>
                components={components}
                rowClassName={() => 'editable-row'}
                bordered
                dataSource={dataSource}
                columns={defaultColumns as ColumnTypes}
                style={{ borderCollapse: 'collapse' }}
            />
        </div>
    );
};

export default AccountEntrySheet;
