import React, { useContext, useEffect, useState } from 'react';
import { type GetRef, Space, type TableProps } from 'antd';
import { Button, Form, Input, Popconfirm, Table } from 'antd';
import {QueryClient, useQuery, useQueryClient} from "@tanstack/react-query";
import {
    getAccountEntries,
    getAccountEntry,
    getConvertedFullAccountEntriesAndRelationships
} from "../features/accountentry/api.ts";
import {techEntryKeys} from "../features/accountentry/keys.ts";
import {DataTypeKind} from "../features/accountentry/types.ts";

type FormInstance<T> = GetRef<typeof Form<T>>;


// 행 타입 단일화
interface DataType {
    key: React.Key;
    node_title: string;
    connected_node_title: string;
    row_data_type: DataTypeKind;
}

// Context도 행 타입으로
const EditableContext = React.createContext<FormInstance<DataType> | null>(null);

// Editable Row
interface EditableRowProps {
    index: number;
}

const EditableRow: React.FC<EditableRowProps> = ({ index, ...props }) => {
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

const shouldShowNodeTitle = (r: DataType) => r.row_data_type === DataTypeKind.Node;
const shouldShowConnectedNodeTitle = (r: DataType) => r.row_data_type === DataTypeKind.Linked;

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
            form.setFieldsValue({ [dataIndex]: record[dataIndex] } as any);
        }
    }, [form, dataIndex, record, editable]);

    const save = async () => {
        try {
            const values = await form.validateFields();
            handleSave({ ...record, ...values });
        } catch (errInfo) {
            console.log('Save failed:', errInfo);
        }
    };

    let childNode = children;

    if(dataIndex == "node_title" && (record.row_data_type === DataTypeKind.Linked)) {
        return <td></td>;
    }

    if(dataIndex == "connected_node_title" && (record.row_data_type === DataTypeKind.Node)) {
        return <td></td>;
    }


    if (editable) {
        childNode = (
            <Form.Item
                style={{ margin: 0 }}
                name={dataIndex as string}
                rules={[{ required: false, message: `${title} is required.` }]}
            >
                <Input.TextArea
                    id={`${record.key}_${String(dataIndex)}`}
                    onPressEnter={(e) => {
                        e.preventDefault(); // 줄바꿈 방지
                        save();
                    }}
                    onBlur={save}
                    autoSize={{ minRows: 1, maxRows: 6 }}
                    style={{
                        width: '100%',
                        margin: 0,
                        border: 'none',
                        borderRadius: 0,
                        boxShadow: 'none',
                        padding: '0 8px',
                        minHeight: '100%',
                        background: 'transparent',
                        resize: 'none',
                    }}
                />
            </Form.Item>
        );
    }
    return <td {...restProps}>{childNode}</td>;
};

type ColumnTypes = Exclude<TableProps<DataType>['columns'], undefined>;

const TechSheet: React.FC = () => {
    const [dataSource, setDataSource] = useState<DataType[]>([
        { key: '0', node_title: 'Edwargfgd King 0', connected_node_title: 'ABCD' , row_data_type: DataTypeKind.Node},
        { key: '1', node_title: 'Edward King 1', connected_node_title: 'EFGH' , row_data_type: DataTypeKind.Node},
    ]);
    const [count, setCount] = useState(2);

    const { data, isLoading, error } = useQuery({
        queryKey: techEntryKeys.all,     // 캐싱 키
        queryFn: getConvertedFullAccountEntriesAndRelationships,     // 실제 호출 함수
    });

    useEffect(() => {
        if(data) {
            setDataSource(data)
        }
    }, [data]);


    if (isLoading) return <p>로딩중...</p>;
    if (error) return <p>에러 발생!</p>;


    const handleDelete = (key: React.Key) => {
        setDataSource((prev) => prev.filter((item) => item.key !== key));
    };

    // 특정 행(record) 아래에 연결 노드 추가
    const handleAddConnectedNode = (record: DataType) => {
        const newRow: DataType = {
            key: count, // React.Key 허용이라 number도 OK
            node_title: 'ABCD',
            connected_node_title: '32',
            row_data_type: DataTypeKind.Linked,
        };

        setDataSource((prev) => {
            const result: DataType[] = [];
            for (const item of prev) {
                result.push(item);
                if (item.key === record.key) {
                    result.push(newRow);
                }
            }
            return result;
        });
        setCount((c) => c + 1);
    };

    const defaultColumns: (ColumnTypes[number] & {
        editable?: boolean;
        dataIndex: keyof DataType;
    })[] = [
        {
            title: 'node_title',
            dataIndex: 'node_title',
            width: '30%',
            editable: true,
            onCell: (record: DataType) => ({
                record,
                editable: record.row_data_type === DataTypeKind.Node, // 행 조건에 따른 편집 여부
                dataIndex: 'node_title',
                title: 'node_title',
                handleSave, // 상위의 저장 핸들러
            }),
        },
        {
            title: 'connected_node_title',
            dataIndex: 'connected_node_title',
            editable: true,
            onCell: (record: DataType) => ({
                record,
                editable: record.row_data_type === DataTypeKind.Linked,
                dataIndex: 'connected_node_title',
                title: 'connected_node_title',
                handleSave,
            }),
        },
        {
            title: 'row_data_type',
            dataIndex: 'row_data_type',
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
            dataIndex: 'operation' as any,
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
                        if (record.row_data_type === DataTypeKind.Node) {
                            return (
                                <Space split="|">
                                    <Popconfirm title="Sure to delete?" onConfirm={() => handleDelete(record.key)}>
                                        <a>항목 삭제</a>
                                    </Popconfirm>
                                    <a onClick={() => handleAddConnectedNode(record)}>
                                        연결된 항목 추가
                                    </a>
                                </Space>
                            );
                        }
                        else if(record.row_data_type === DataTypeKind.Linked){
                            return (
                                <Space split="|">
                                    <Popconfirm title="Sure to delete?" onConfirm={() => handleDelete(record.key)}>
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

    const handleAdd = () => {
        const newData: DataType = {
            key: count,
            node_title: `Edward King ${count}`,
            connected_node_title: '32',
            row_data_type: DataTypeKind.Node,
        };
        setDataSource((prev) => [...prev, newData]);
        setCount((c) => c + 1);
    };

    const handleSave = (row: DataType) => {
        setDataSource((prev) => {
            const idx = prev.findIndex((item) => item.key === row.key);
            if (idx === -1) return prev;
            const next = prev.slice();
            next.splice(idx, 1, { ...prev[idx], ...row });
            return next;
        });
    };

    const components = {
        body: {
            row: EditableRow,
            cell: EditableCell,
        },
    };

    const columns = defaultColumns

    return (
        <div>
            <Button onClick={handleAdd} type="primary" style={{ marginBottom: 16 }}>
                노드 항목 추가
            </Button>
            <Table<DataType>
                components={components}
                rowClassName={() => 'editable-row'}
                bordered
                dataSource={dataSource}
                columns={columns as ColumnTypes}
            />
        </div>
    );
};

export default TechSheet;
