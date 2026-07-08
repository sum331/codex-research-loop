import type { EdgeId, GraphAggregationMarker, GraphData, GraphFocusInput, GraphPinHint, GraphTypeFilters, NodeId, PinMap, SelectionInput, ThemeId } from "../types";
import { type GraphWorldBounds } from "./geometry";
export type DensityMode = "card" | "compact-card" | "point-plus-focus" | "overview";
export type NodeDisplayMode = "card" | "compact-card" | "point" | "overview";
export type NodeVisualRole = "landmark" | "index-slip" | "cinnabar-note" | "map-pin";
export type GraphRenderBudgetView = "global" | "community";
export type GraphCommunityFocusSizeBand = "small" | "medium" | "large" | "oversized";
export type GraphCommunityFocusRepresentation = "cards-and-labels" | "points-with-cards" | "outline-with-caps" | "internal-map-entry";
export type GraphCommunityQualityLevel = "good" | "moderate" | "poor";
export type GraphCommunityBoundaryCertainty = "high" | "reduced" | "low";
export type GraphCommunityQualitySignalId = "oversized-community" | "many-tiny-communities" | "mixed-cross-community-edges" | "weak-community-labels" | "abnormal-community-count";
export interface GraphRenderBudgetLimits {
    maxVisibleNodes: number;
    maxVisibleEdges: number;
    maxLabels: number;
    maxCards: number;
    maxInteractionUpdates: number;
}
export interface GraphRenderBudget {
    view: GraphRenderBudgetView;
    limits: GraphRenderBudgetLimits;
    usage: GraphRenderBudgetLimits;
}
export interface GraphRenderOverflowBucket {
    total: number;
    hidden: number;
    ids: string[];
}
export interface GraphRenderOverflow {
    nodes: GraphRenderOverflowBucket;
    edges: GraphRenderOverflowBucket;
    labels: GraphRenderOverflowBucket;
    cards: GraphRenderOverflowBucket;
    interactionUpdates: {
        total: number;
        hidden: number;
    };
}
export interface GraphInteractionDegradation {
    mode: "idle" | "active";
    maxUpdatedObjects: number;
    updateCandidates: number;
    updatedObjects: number;
    hiddenObjects: number;
    labelsVisibleDuringInteraction: number;
    edgesVisibleDuringInteraction: number;
    preservedNodeIds: string[];
}
export interface GraphCommunityFocusScale {
    communityId: string;
    nodeCount: number;
    sizeBand: GraphCommunityFocusSizeBand;
    representation: GraphCommunityFocusRepresentation;
    completePresence: "nodes" | "outline" | "internal-map";
    thresholds: {
        smallMax: number;
        mediumMax: number;
        largeMax: number;
    };
}
export interface GraphCommunityQualitySignal {
    id: GraphCommunityQualitySignalId;
    severity: "moderate" | "poor";
    value: number;
    threshold: number;
}
export interface GraphCommunityAuxiliaryView {
    id: "core-structure-connectivity";
    label: "核心结构 / 连通性";
}
export interface GraphCommunityQuality {
    level: GraphCommunityQualityLevel;
    boundaryCertainty: GraphCommunityBoundaryCertainty;
    warning: "moderate-community-quality" | "poor-community-quality" | null;
    signals: GraphCommunityQualitySignal[];
    auxiliaryViews: GraphCommunityAuxiliaryView[];
}
export interface RenderableGraph {
    model: Record<string, unknown>;
    layout: Record<string, unknown>;
    worldBounds: GraphWorldBounds;
    selectedNodeId: string | null;
    focus: GraphFocusInput;
    typeFilters: GraphTypeFilters;
    densityMode: DensityMode;
    counts: {
        visibleNodes: number;
        visibleEdges: number;
        totalNodes: number;
        totalEdges: number;
        totalCommunities: number;
    };
    nodes: RenderableNode[];
    edges: RenderableEdge[];
    communities: RenderableCommunity[];
    aggregationContainers: RenderableAggregationContainer[];
    minimap: RenderableMinimap;
    budget: GraphRenderBudget;
    overflow: GraphRenderOverflow;
    interaction: GraphInteractionDegradation;
    importance: {
        stableCoreNodeIds: string[];
        stableSkeletonEdgeIds: string[];
        temporaryBoostNodeIds: string[];
    };
    communityFocus: GraphCommunityFocusScale | null;
    communityQuality: GraphCommunityQuality;
    communityMap: GraphCommunityMapRules;
}
export interface RenderableNode {
    id: string;
    label: string;
    type: string;
    kind: string;
    community: string;
    sourcePath: string;
    x: number;
    y: number;
    point: {
        x: number;
        y: number;
    };
    displayMode: NodeDisplayMode;
    visualRole: NodeVisualRole;
    priority: number;
    weight: number;
    stableImportance: number;
    temporaryBoost: number;
    coreAnchor: boolean;
    unavailable: boolean;
    selected: boolean;
    startNode: boolean;
    previewStart: boolean;
    labelVisible: boolean;
    interactionLabelVisible: boolean;
    communityMapImportance: number;
    communityMapDotSize: number;
    communityMapLabelSide: "left" | "right" | "top" | "bottom";
    communityMapRelationLabel: boolean;
    communityMapTier: CommunityMapNodeTier;
    communityColor: string;
}
export interface RenderableEdge {
    id: string;
    source: string;
    target: string;
    type: string;
    confidence: string;
    relationType: string;
    relationClass: string;
    path: string;
    curveOffset: number;
    strokeWidth: number;
    opacity: number;
    simulationWeight: number;
    skeleton: boolean;
    traceable: boolean;
    communityMapLayer: CommunityMapEdgeLayer;
}
export interface RenderableCommunity {
    id: string;
    label: string;
    color: string;
    nodeCount: number;
    boundaryCertainty: GraphCommunityBoundaryCertainty;
    wash: {
        cx: number;
        cy: number;
        rx: number;
        ry: number;
        opacity: number;
    } | null;
}
export interface RenderableAggregationContainer {
    id: string;
    role: "aggregation-container";
    label: string;
    communityId: string | null;
    nodeIds: string[];
    nodeCount: number;
    searchHitCount: number;
    pinnedCount: number;
    selectedCount: number;
    selected: boolean;
    searchResultIds: string[];
    pinnedNodeIds: string[];
    selectedNodeIds: string[];
    pinHints: GraphPinHint[];
    point: {
        x: number;
        y: number;
    };
    x: number;
    y: number;
    radius: number;
    color: string;
}
export interface RenderableMinimap {
    path: string;
    nodes: Array<{
        id: string;
        x: number;
        y: number;
        r: number;
        fill: string;
        selected: boolean;
    }>;
}
export type CommunityMapNodeTier = "core" | "related" | "peripheral";
export type CommunityMapEdgeLayer = "skeleton" | "related" | "background";
export type CommunityMapMotionMode = "live" | "frozen";
export type CommunityMapLabelSide = "left" | "right" | "top" | "bottom";
export interface CommunityMapNodeRule {
    nodeId: NodeId;
    tier: CommunityMapNodeTier;
    basePoint: RenderPosition;
    labelVisible: boolean;
    labelSide: CommunityMapLabelSide;
    relationLabel: boolean;
    importance: number;
    dotSize: number;
}
export interface CommunityMapEdgeRule {
    edgeId: EdgeId;
    layer: CommunityMapEdgeLayer;
    skeleton: boolean;
    traceable: boolean;
}
export interface CommunityMapLayoutSnapshot {
    coordinateSpace: "world";
    bounds: {
        minX: number;
        minY: number;
        maxX: number;
        maxY: number;
        width: number;
        height: number;
    };
    viewportAspectRatio: number | null;
}
export interface CommunityMapRuleSnapshot {
    communityId: string;
    source: "focus" | "source-context";
    nodeRulesById: Record<NodeId, CommunityMapNodeRule>;
    edgeRulesById: Record<EdgeId, CommunityMapEdgeRule>;
    layout: CommunityMapLayoutSnapshot;
    labelBudget: {
        limit: number;
        visible: number;
        hidden: number;
    };
    edgeLayers: Record<CommunityMapEdgeLayer, number>;
}
export interface GraphCommunityMapRules {
    active: boolean;
    sourceCommunityId: string | null;
    motionMode: CommunityMapMotionMode;
    maxNodeDriftRatio: number;
    current: CommunityMapRuleSnapshot | null;
    rulesByCommunityId: Record<string, CommunityMapRuleSnapshot>;
}
interface BuildRenderableGraphOptions {
    pins?: PinMap;
    theme?: ThemeId;
    selectedNodeId?: string | null;
    selection?: SelectionInput | null;
    focus?: GraphFocusInput;
    typeFilters?: GraphTypeFilters;
    positions?: RenderPositionMap;
    pathCache?: RenderPathCache;
    searchResultIds?: NodeId[];
    aggregationMarkers?: GraphAggregationMarker[];
    viewportSize?: {
        width: number;
        height: number;
    };
    sourceCommunityId?: string | null;
}
type AtlasNode = {
    id: string;
    label: string;
    type: string;
    kind: string;
    community: string;
    source_path?: string;
    x: number;
    y: number;
    priority?: number;
    weight?: number;
    unavailable?: boolean;
};
export interface RenderPosition {
    x: number;
    y: number;
}
export type RenderPositionMap = Record<NodeId, RenderPosition>;
export interface RenderPathCache {
    getEdgeCurve(edge: {
        id: string;
        source: string;
        target: string;
        weight?: number;
    }, source: RenderPosition, target: RenderPosition): number;
    clear(): void;
}
export declare const GRAPH_RENDER_BUDGETS: Record<GraphRenderBudgetView, GraphRenderBudgetLimits>;
export declare const GRAPH_COMMUNITY_FOCUS_THRESHOLDS: {
    readonly smallMax: 40;
    readonly mediumMax: 250;
    readonly largeMax: 1000;
};
export declare const GRAPH_COMMUNITY_FOCUS_BUDGETS: Record<GraphCommunityFocusSizeBand, GraphRenderBudgetLimits>;
export declare function createRenderPathCache(): RenderPathCache;
export declare function buildRenderableGraph(data: GraphData, options?: BuildRenderableGraphOptions): RenderableGraph;
export declare function evaluateCommunityQuality(data: GraphData): GraphCommunityQuality;
export declare function resolveGraphRenderBudget(focus: GraphFocusInput, focusedCommunityNodeCount?: number): GraphRenderBudgetLimits;
export declare function resolveCommunityFocusScale(focus: GraphFocusInput, focusedCommunityNodeCount: number): GraphCommunityFocusScale | null;
export declare function makeEdgePath(source: AtlasNode, target: AtlasNode, edge: {
    weight?: number;
}): string;
export declare function makeEdgePathFromPoints(sourcePoint: RenderPosition, targetPoint: RenderPosition, curveOffset: number): string;
export declare function edgeStrokeWidth(edge: {
    weight?: number;
}): number;
export declare function edgeOpacity(edge: {
    weight?: number;
}): number;
export declare function edgeVisualStrokeWidth(edge: {
    weight?: number;
}, focusedView: boolean): number;
export declare function edgeVisualOpacity(edge: {
    weight?: number;
}, focusedView: boolean): number;
export declare function edgeRelationClass(relationType: unknown): string;
export declare function screenEffectiveDensityMode(visibleNodeCount: number, viewportScale: number): DensityMode;
export declare function nodeDisplayModeForDensity(node: Pick<RenderableNode, "selected" | "labelVisible" | "visualRole">, densityMode: DensityMode): NodeDisplayMode;
export {};
//# sourceMappingURL=model.d.ts.map