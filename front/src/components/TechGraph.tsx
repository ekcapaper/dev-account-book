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
        <div>
            <div style={{ width: '400px', height: '200px', border: '1px solid black' }}>
                <ForceGraph2D
                    graphData={data}
                    nodeLabel="name"           // 마우스 올렸을 때 라벨 표시
                    nodeAutoColorBy="id"       // 노드마다 자동 색상
                    width={400}
                    height={200}
                />
            </div>
        </div>
    );
}
