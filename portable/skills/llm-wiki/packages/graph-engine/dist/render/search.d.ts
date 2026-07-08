import type { GraphNode, NodeId } from "../types";
export type GraphSearchNodeState = "none" | "match" | "faded";
export interface GraphSearchNodeView {
    id: NodeId;
    searchState: GraphSearchNodeState;
}
export interface GraphSearchState {
    query: string;
    matchIds: NodeId[];
    nodes: GraphSearchNodeView[];
    searchIndex: Array<{
        node: GraphNode;
        haystack: string;
    }>;
}
export interface GraphSearchFocus {
    id: NodeId | null;
    index: number;
}
export declare function resolveGraphSearchState(nodes: GraphNode[], query: string, cachedIndex?: Array<{
    node: GraphNode;
    haystack: string;
}>): GraphSearchState;
export declare function resolveNextGraphSearchFocus(matchIds: NodeId[], currentId: NodeId | null | undefined): GraphSearchFocus;
export declare function resolvePreviousGraphSearchFocus(matchIds: NodeId[], currentId: NodeId | null | undefined): GraphSearchFocus;
//# sourceMappingURL=search.d.ts.map