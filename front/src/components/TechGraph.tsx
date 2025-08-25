import ForceGraph2D from 'react-force-graph-2d';

const data = {
    nodes: [
        { id: 'A', name: 'Node A' },
        { id: 'B', name: 'Node B' },
        { id: 'C', name: 'Node C' },
    ],
    links: [
        { source: 'A', target: 'B' },
        { source: 'B', target: 'C' },
        { source: 'C', target: 'A' },
    ],
};

export default function TechGraph() {
    return (
        <div style={{ width: '600px', height: '400px' }}>
            <ForceGraph2D
                graphData={data}
                nodeLabel="name"           // 마우스 올렸을 때 라벨 표시
                nodeAutoColorBy="id"       // 노드마다 자동 색상
            />
        </div>
    );
}
