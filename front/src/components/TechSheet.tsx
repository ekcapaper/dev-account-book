import React, { useContext, useEffect, useRef, useState } from 'react';
import {type GetRef, type InputRef, Space, type TableProps} from 'antd';
import { Button, Form, Input, Popconfirm, Table } from 'antd';

type FormInstance<T> = GetRef<typeof Form<T>>;

// Editable Row
const EditableContext = React.createContext<FormInstance<any> | null>(null);

interface EditableRowProps {
    index: number;
}

const EditableRow: React.FC<EditableRowProps> = ({ index, ...props }) => {
    const [form] = Form.useForm();
    return (
        <Form form={form} component={false}>
            <EditableContext.Provider value={form}>
                <tr {...props} />
            </EditableContext.Provider>
        </Form>
    );
};

// Editable Cell
interface Item {
    key: string;
    node_title: string;
    connected_node_title: string;
}

interface EditableCellProps {
    title: React.ReactNode;
    editable: boolean;
    dataIndex: keyof Item;
    record: Item;
    handleSave: (record: Item) => void;
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
    const [editing, setEditing] = useState(false);
    const inputRef = useRef<InputRef>(null);
    const form = useContext(EditableContext)!;
    
    // 항상 열린 셀: 마운트/레코드 변경 시 기본값 주입
    useEffect(() => {
        if(editable) {
            form.setFieldsValue({[dataIndex]: record[dataIndex]});
        }
    }, [form, dataIndex, record, editable]);


    const toggleEdit = () => {
        setEditing(!editing);
        form.setFieldsValue({ [dataIndex]: record[dataIndex] });
    };

    const save = async () => {
        try {
            const values = await form.validateFields();

            toggleEdit();
            handleSave({ ...record, ...values });
        } catch (errInfo) {
            console.log('Save failed:', errInfo);
        }
    };

    let childNode = children;

    if (editable) {
        childNode = (
            <Form.Item
                style={{ margin: 0 }}
                name={dataIndex}
                rules={[{ required: false, message: `${title} is required.` }]}
            >
                <Input.TextArea
                    id={`${record.key}_${dataIndex}`}
                    onPressEnter={save}
                    onBlur={save}
                    autoSize={{ minRows: 1, maxRows: 6 }} // 글자수에 맞춰 행 높이 자동 조정
                    style={{
                        width: '100%',
                        margin: 0,
                        border: 'none',
                        borderRadius: 0,
                        boxShadow: 'none',
                        padding: '0 8px',
                        minHeight: '100%',
                        background: 'transparent',
                        resize: 'none', // 사용자가 수동으로 크기 조정 못 하게
                    }}

                />
            </Form.Item>
        )
    }
    return <td  {...restProps}>{childNode}</td>;
};


// Tech Sheet
interface DataType {
    key: React.Key;
    node_title: string;
    connected_node_title: string;
}

type ColumnTypes = Exclude<TableProps<DataType>['columns'], undefined>;

const TechSheet: React.FC = () => {
    const [dataSource, setDataSource] = useState<DataType[]>([
        {
            key: '0',
            node_title: 'Edwargfgd King 0',
            connected_node_title: '',
        },
        {
            key: '1',
            node_title: 'Edward King 1',
            connected_node_title: '',
        },
    ]);

    const [count, setCount] = useState(2);

    const handleDelete = (key: React.Key) => {
        const newData = dataSource.filter((item) => item.key !== key);
        setDataSource(newData);
    };

    // temp code
    const handleAddConnectedNode = (record) => {
        const newData: DataType = {
            key: count,
            node_title: ``,
            connected_node_title: '32',
        };
        console.log(record)
        let dataSourceNew = [];
        for (const item of dataSource) {
            dataSourceNew.push(item);

            if (item.node_title === record.node_title) {
                dataSourceNew.push(newData);
            }
        }

        setDataSource(dataSourceNew);
        setCount(count + 1);
    };

    const defaultColumns: (ColumnTypes[number] & { editable?: boolean; dataIndex: string })[] = [
        {
            title: 'node_title',
            dataIndex: 'node_title',
            width: '30%',
            editable: true,
        },
        {
            title: 'connected_node_title',
            dataIndex: 'connected_node_title',
            editable: true,
        },
        {
            title: 'operation',
            dataIndex: 'operation',
            render: (_, record) =>
                dataSource.length >= 1 ? (
                    <div>
                        <Space split={"|"}>
                            <a onClick={() => handleAddConnectedNode(record)}>연결된 항목 추가</a>
                            <Popconfirm title="Sure to delete?" onConfirm={() => handleDelete(record)}>
                                <a>삭제</a>
                            </Popconfirm>
                        </Space>
                    </div>
                ) : null,
        },
    ];

    const handleAdd = () => {
        const newData: DataType = {
            key: count,
            node_title: `Edward King ${count}`,
            connected_node_title: '32',
        };
        setDataSource([...dataSource, newData]);
        setCount(count + 1);
    };

    const handleSave = (row: DataType) => {
        const newData = [...dataSource];
        const index = newData.findIndex((item) => row.key === item.key);
        const item = newData[index];
        newData.splice(index, 1, {
            ...item,
            ...row,
        });
        setDataSource(newData);
    };

    const components = {
        body: {
            row: EditableRow,
            cell: EditableCell,
        },
    };

    const columns = defaultColumns.map((col) => {
        if (!col.editable) {
            return col;
        }
        return {
            ...col,
            onCell: (record: DataType) => ({
                record,
                editable: col.editable,
                dataIndex: col.dataIndex,
                title: col.title,
                handleSave,
            }),
        };
    });

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