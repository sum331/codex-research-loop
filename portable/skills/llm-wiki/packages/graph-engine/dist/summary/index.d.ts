import type { CommunityId, GraphAggregationMarker, GraphCommunitySummaryPayload, GraphData, GraphExcludedObjectPayload, GraphGlobalOverviewPayload, GraphNodeSummaryPayload, GraphSearchResultsPayload, GraphSummaryObjectRef, GraphSummaryOptions, GraphUnavailableObjectPayload, NodeId, PinMap } from "../types";
export declare function summarizeGraphNode(data: GraphData, nodeId: NodeId, options?: GraphSummaryOptions): GraphNodeSummaryPayload | GraphUnavailableObjectPayload;
export declare function summarizeGraphCommunity(data: GraphData, communityId: CommunityId, options?: GraphSummaryOptions): GraphCommunitySummaryPayload | GraphUnavailableObjectPayload;
export declare function summarizeGraphGlobal(data: GraphData, options?: GraphSummaryOptions): GraphGlobalOverviewPayload;
export declare function summarizeGraphSearchResults(data: GraphData, query: string, resultIds: NodeId[], options?: GraphSummaryOptions): GraphSearchResultsPayload;
export declare function summarizeExcludedGraphObject(data: GraphData, object: GraphSummaryObjectRef, reason: GraphExcludedObjectPayload["reason"], options?: GraphSummaryOptions): GraphExcludedObjectPayload;
export declare function summarizeUnavailableGraphObject(data: GraphData, object: GraphSummaryObjectRef, reason: GraphUnavailableObjectPayload["reason"], options?: GraphSummaryOptions): GraphUnavailableObjectPayload;
export declare function buildCommunityAggregationMarkers(data: GraphData, options?: {
    pins?: PinMap;
    minCommunitySize?: number;
}): GraphAggregationMarker[];
//# sourceMappingURL=index.d.ts.map