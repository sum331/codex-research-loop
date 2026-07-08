export type GraphSpatialHitKind = "node" | "edge" | "community-wash" | "aggregation-container" | "graph-blank";
export interface GraphSpatialPoint {
    x: number;
    y: number;
}
export interface GraphSpatialRect {
    x: number;
    y: number;
    width: number;
    height: number;
}
export interface GraphSpatialNodeLike {
    id: string;
    label?: string;
    type?: string;
    displayMode?: string;
    visualRole?: string;
    point?: GraphSpatialPoint;
    x?: number;
    y?: number;
    hitBounds?: GraphSpatialRect;
}
export interface GraphSpatialEdgeLike {
    id: string;
    source: string;
    target: string;
    curveOffset?: number;
}
export interface GraphSpatialCommunityLike {
    id: string;
    wash?: {
        cx: number;
        cy: number;
        rx: number;
        ry: number;
    } | null;
}
export interface GraphSpatialAggregationContainerLike {
    id: string;
    communityId?: string | null;
    point?: GraphSpatialPoint;
    radius?: number;
}
export type GraphSpatialHitTarget = {
    kind: "node";
    id: string;
} | {
    kind: "edge";
    id: string;
} | {
    kind: "community-wash";
    id: string;
} | {
    kind: "aggregation-container";
    id: string;
    communityId: string | null;
} | {
    kind: "graph-blank";
};
export interface GraphSpatialIndexInput {
    nodes?: readonly GraphSpatialNodeLike[];
    edges?: readonly GraphSpatialEdgeLike[];
    communities?: readonly GraphSpatialCommunityLike[];
    aggregationContainers?: readonly GraphSpatialAggregationContainerLike[];
    edgeHitTolerance?: number;
    nodeFallbackRadius?: number;
}
interface SpatialNodeEntry {
    id: string;
    point: GraphSpatialPoint;
    bounds: GraphSpatialRect;
    radius: number;
    order: number;
}
interface SpatialEdgeEntry {
    id: string;
    source: GraphSpatialPoint;
    target: GraphSpatialPoint;
    curveOffset: number;
    bounds: GraphSpatialRect;
    order: number;
}
interface SpatialCommunityEntry {
    id: string;
    cx: number;
    cy: number;
    rx: number;
    ry: number;
    order: number;
}
interface SpatialAggregationContainerEntry {
    id: string;
    communityId: string | null;
    point: GraphSpatialPoint;
    radius: number;
    order: number;
}
export declare const DEFAULT_GRAPH_EDGE_HIT_TOLERANCE = 10;
export declare const DEFAULT_GRAPH_NODE_FALLBACK_RADIUS = 32;
export declare class GraphSpatialIndex {
    private readonly nodes;
    private readonly edges;
    private readonly communities;
    private readonly aggregationContainers;
    private readonly nodeTree;
    private readonly edgeGrid;
    private readonly maxNodeRadius;
    private readonly edgeHitTolerance;
    private readonly nodeFallbackRadius;
    constructor(input?: GraphSpatialIndexInput);
    rebuild(input: GraphSpatialIndexInput): GraphSpatialIndex;
    hitTest(point: GraphSpatialPoint): GraphSpatialHitTarget;
    findNode(point: GraphSpatialPoint): SpatialNodeEntry | null;
    findEdge(point: GraphSpatialPoint): SpatialEdgeEntry | null;
    findCommunity(point: GraphSpatialPoint): SpatialCommunityEntry | null;
    findAggregationContainer(point: GraphSpatialPoint): SpatialAggregationContainerEntry | null;
    nearestNode(point: GraphSpatialPoint, radius?: number): SpatialNodeEntry | null;
    edgeCandidateCount(point: GraphSpatialPoint): number;
    private collectNodeCandidates;
    private visitEdgeCandidates;
}
export declare function createGraphSpatialIndex(input?: GraphSpatialIndexInput): GraphSpatialIndex;
export {};
//# sourceMappingURL=spatial-index.d.ts.map