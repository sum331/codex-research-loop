export type GraphRelationFocusDepth = "none" | "focus" | "first" | "second" | "unrelated";
export interface GraphRelationFocusNodeLike {
    id: string;
}
export interface GraphRelationFocusEdgeLike {
    id: string;
    source: string;
    target: string;
}
export interface ResolveGraphRelationFocusInput {
    activeNodeId: string | null;
    nodes: GraphRelationFocusNodeLike[];
    edges: GraphRelationFocusEdgeLike[];
}
export interface GraphRelationFocusState {
    activeNodeId: string | null;
    nodeDepthById: Map<string, GraphRelationFocusDepth>;
    edgeDepthById: Map<string, GraphRelationFocusDepth>;
    firstNodeIds: Set<string>;
    secondNodeIds: Set<string>;
    directEdgeIds: Set<string>;
}
export declare function resolveGraphRelationFocus(input: ResolveGraphRelationFocusInput): GraphRelationFocusState;
//# sourceMappingURL=relation-focus.d.ts.map