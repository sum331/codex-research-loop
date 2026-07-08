import type { CommunityId, Confidence, EdgeId, GraphAggregationMarker, GraphData, GraphNodeType, GraphPinHint, GraphRelationType, GraphSummaryCommand, GraphSummaryObjectRef, GraphSummarySelectionState, GraphTypeFilters, GraphFocusInput, NodeId, PinMap, SelectionInput, ThemeId, WikiPath } from "../types";
import { type CommunityMapEdgeLayer, type CommunityMapLabelSide, type CommunityMapNodeTier, type RenderPosition, type RenderPositionMap, type RenderableGraph } from "./model";
export declare const GRAPH_RENDERER_ADAPTER_ROUTES: readonly ["dom-svg", "candidate-global", "aggregation-fallback"];
export type GraphRendererAdapterRoute = typeof GRAPH_RENDERER_ADAPTER_ROUTES[number];
export interface GraphRendererAdapterOptions {
    theme?: ThemeId;
    pins?: PinMap;
    selection?: SelectionInput | null;
    searchResultIds?: NodeId[];
    aggregationMarkers?: GraphAggregationMarker[];
    focus?: GraphFocusInput;
    typeFilters?: GraphTypeFilters;
    positions?: RenderPositionMap;
    sourceCommunityId?: string | null;
}
export interface GraphRendererAdapterData {
    renderable: RenderableGraph;
    counts: RenderableGraph["counts"];
    selection: GraphSummarySelectionState;
    sourceCommunityId: string | null;
    nodes: GraphRendererAdapterNode[];
    edges: GraphRendererAdapterEdge[];
    communities: GraphRendererAdapterCommunity[];
    aggregations: GraphRendererAdapterAggregation[];
}
export interface GraphRendererDrawerTarget {
    summaryKind: "node-summary" | "community-summary" | "excluded-object";
    object: GraphSummaryObjectRef;
    reason?: "aggregation";
}
export interface GraphRendererAdapterNode {
    id: NodeId;
    object: {
        kind: "node";
        nodeId: NodeId;
    };
    label: string;
    type: GraphNodeType;
    communityId: CommunityId | null;
    sourcePath: WikiPath;
    point: RenderPosition;
    selected: boolean;
    searchHit: boolean;
    pinHint: GraphPinHint;
    aggregationIds: string[];
    drawerTarget: GraphRendererDrawerTarget;
    render: {
        displayMode: string;
        visualRole: string;
        priority: number;
        labelVisible: boolean;
        communityMapTier: CommunityMapNodeTier;
        communityMapImportance: number;
        communityMapDotSize: number;
        communityMapLabelSide: CommunityMapLabelSide;
        communityMapRelationLabel: boolean;
    };
}
export interface GraphRendererAdapterEdge {
    id: EdgeId;
    sourceNodeId: NodeId;
    targetNodeId: NodeId;
    sourceCommunityId: CommunityId | null;
    targetCommunityId: CommunityId | null;
    relationType: GraphRelationType | null;
    confidence: Confidence | null;
    weight: number;
    render: {
        strokeWidth: number;
        opacity: number;
        communityMapLayer: CommunityMapEdgeLayer;
        skeleton: boolean;
        traceable: boolean;
    };
}
export interface GraphRendererAdapterCommunity {
    id: CommunityId;
    object: {
        kind: "community";
        communityId: CommunityId;
    };
    label: string;
    nodeIds: NodeId[];
    nodeCount: number;
    selected: boolean;
    searchResultIds: NodeId[];
    pinHints: GraphPinHint[];
    aggregationIds: string[];
    drawerTarget: GraphRendererDrawerTarget;
    commands: GraphSummaryCommand[];
}
export interface GraphRendererAdapterAggregation {
    id: string;
    object: {
        kind: "aggregation";
        aggregationId: string;
        nodeIds: NodeId[];
        communityId?: CommunityId | null;
    };
    label: string;
    communityId: CommunityId | null;
    nodeIds: NodeId[];
    selectedNodeIds: NodeId[];
    searchResultIds: NodeId[];
    pinnedNodeIds: NodeId[];
    totalCount: number;
    selected: boolean;
    pinHints: GraphPinHint[];
    drawerTarget: GraphRendererDrawerTarget;
    commands: GraphSummaryCommand[];
}
export interface GraphRendererBehaviorContract {
    route: GraphRendererAdapterRoute;
    pointSelect: GraphRendererPointSelectBehavior[];
    containerSelect: GraphRendererContainerSelectBehavior[];
    searchHighlight: GraphRendererSearchHighlightBehavior[];
    selectedObjectInsideAggregation: GraphRendererSelectedAggregationBehavior[];
    pinInsideAggregation: GraphRendererPinnedAggregationBehavior[];
    enterCommunity: GraphRendererEnterCommunityBehavior[];
}
export interface GraphRendererPointSelectBehavior {
    nodeId: NodeId;
    object: {
        kind: "node";
        nodeId: NodeId;
    };
    drawerTarget: GraphRendererDrawerTarget;
    selected: boolean;
    searchHit: boolean;
    pinHint: GraphPinHint;
    aggregationIds: string[];
}
export interface GraphRendererContainerSelectBehavior {
    containerId: CommunityId | string;
    object: GraphSummaryObjectRef;
    drawerTarget: GraphRendererDrawerTarget;
    selected: boolean;
    searchResultIds: NodeId[];
    pinHintNodeIds: NodeId[];
}
export interface GraphRendererSearchHighlightBehavior {
    nodeId: NodeId;
    object: {
        kind: "node";
        nodeId: NodeId;
    };
    aggregationIds: string[];
    drawerTarget: GraphRendererDrawerTarget;
}
export interface GraphRendererSelectedAggregationBehavior {
    aggregationId: string;
    object: {
        kind: "aggregation";
        aggregationId: string;
        nodeIds: NodeId[];
        communityId?: CommunityId | null;
    };
    selectedNodeIds: NodeId[];
    selected: boolean;
    drawerTarget: GraphRendererDrawerTarget;
}
export interface GraphRendererPinnedAggregationBehavior {
    aggregationId: string;
    pinnedNodeIds: NodeId[];
    pinHints: GraphPinHint[];
    drawerTarget: GraphRendererDrawerTarget;
}
export interface GraphRendererEnterCommunityBehavior {
    communityId: CommunityId;
    command: Extract<GraphSummaryCommand, {
        kind: "enter-community";
    }>;
}
export declare function buildGraphRendererAdapterData(data: GraphData, options?: GraphRendererAdapterOptions): GraphRendererAdapterData;
export declare function buildGraphRendererBehaviorContract(adapter: GraphRendererAdapterData, route: GraphRendererAdapterRoute): GraphRendererBehaviorContract;
//# sourceMappingURL=adapter.d.ts.map