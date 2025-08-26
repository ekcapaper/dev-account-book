import React from 'react';
import { LaptopOutlined, NotificationOutlined } from '@ant-design/icons';
import {type MenuProps} from 'antd';
import { Layout, Menu, theme } from 'antd';
import {Link, Outlet} from "react-router-dom";

const { Header, Content, Sider } = Layout;


const items2: MenuProps['items'] = [
    {
        key: `menu-home`,
        icon: React.createElement(LaptopOutlined),
        label: <Link to={"/"}>홈 화면</Link>,
    },
    {
        key: `menu-data-crud`,
        icon: React.createElement(LaptopOutlined),
        label: `데이터`,
        children: [
            {
                key: `sub-tech-entry-sheet`,
                icon: React.createElement(NotificationOutlined),
                label: <Link to={"/tech-entry-sheet"}>Tech Sheet</Link>
            },
            /*
            {
                key: `sub-tech-entry-graph`,
                icon: React.createElement(NotificationOutlined),
                label: <Link to={"/tech-entry-graph"}>Tech Graph</Link>
            },
            */
            {
                key: `sub-tech-entry-explore`,
                icon: React.createElement(NotificationOutlined),
                label: <Link to={"/tech-entry-explore"}>Tech Explorer</Link>
            },
        ]
    },
    {
        key: `menu-about`,
        icon: React.createElement(LaptopOutlined),
        label: <Link to={"/about"}>`정보`</Link>,
    }
]

const App: React.FC = () => {
    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Header style={{ display: 'flex', alignItems: 'center', padding: 15, }}>
                <h2 style={{color: 'white'}}>DevAccountBook</h2>
            </Header>

            <Layout>
                <Sider width={200} style={{ background: colorBgContainer }}>
                    <Menu
                        mode="inline"
                        defaultSelectedKeys={['1']}
                        defaultOpenKeys={['sub1']}
                        style={{ height: '100%', borderInlineEnd: 0 }}
                        items={items2}
                    />
                </Sider>
                <Layout style={{ padding: '0 24px 24px' }}>
                    <Content
                        style={{
                            padding: 24,
                            margin: 0,
                            minHeight: 280,
                            background: colorBgContainer,
                            borderRadius: borderRadiusLG,
                        }}
                    >
                        <Outlet/>
                    </Content>
                </Layout>
            </Layout>
        </Layout>
    );
};

export default App;