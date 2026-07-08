import type { GraphEdgeStyleOptions, ThemeId } from "../types";
import type { GraphRendererAdapterAggregation, GraphRendererAdapterCommunity, GraphRendererAdapterData, GraphRendererAdapterEdge, GraphRendererAdapterNode } from "./adapter";
import type { CommunityMapEdgeLayer, CommunityMapNodeTier } from "./model";
import type { SigmaGlobalGraphologyGraph, SigmaGlobalGraphologyRuntime } from "./sigma-global-types";
export interface SigmaGlobalGraphologyNodeAttributes {
    x: number;
    y: number;
    label: string;
    size: number;
    color: string;
    type: string;
    graphNodeType: string;
    communityId: string | null;
    sourcePath: string;
    selected: boolean;
    searchHit: boolean;
    pinned: boolean;
    communityDimmed: boolean;
    communitySpotlightVisible: boolean;
    aggregationIds: string[];
    labelVisible: boolean;
    displayMode: string;
    visualRole: string;
    priority: number;
    communityMapTier: CommunityMapNodeTier;
    communityMapImportance: number;
    drawerTarget: GraphRendererAdapterNode["drawerTarget"];
}
export interface SigmaGlobalGraphologyEdgeAttributes {
    size: number;
    color: string;
    relationType: string | null;
    confidence: string | null;
    weight: number;
    sourceCommunityId: string | null;
    targetCommunityId: string | null;
    communityMapLayer: CommunityMapEdgeLayer;
}
export interface SigmaGlobalGraphologyCommunityAttributes {
    id: string;
    label: string;
    color: string;
    nodeIds: string[];
    nodeCount: number;
    selected: boolean;
    searchResultIds: string[];
    pinnedNodeIds: string[];
    aggregationIds: string[];
    drawerTarget: GraphRendererAdapterCommunity["drawerTarget"];
    commands: GraphRendererAdapterCommunity["commands"];
}
export interface SigmaGlobalGraphologyAggregationAttributes {
    id: string;
    label: string;
    communityId: string | null;
    nodeIds: string[];
    selectedNodeIds: string[];
    searchResultIds: string[];
    pinnedNodeIds: string[];
    totalCount: number;
    selected: boolean;
    color: string;
    point: {
        x: number;
        y: number;
    } | null;
    radius: number | null;
    drawerTarget: GraphRendererAdapterAggregation["drawerTarget"];
    commands: GraphRendererAdapterAggregation["commands"];
}
export interface SigmaGlobalEdgeStyle {
    color: string;
    size: number;
}
export declare function buildSigmaGlobalGraphologyGraph(adapterData: GraphRendererAdapterData, runtime: SigmaGlobalGraphologyRuntime, theme?: ThemeId, edgeStyle?: GraphEdgeStyleOptions): SigmaGlobalGraphologyGraph;
export declare function canPatchSigmaGlobalGraphAttributes(current: GraphRendererAdapterData, next: GraphRendererAdapterData, currentTheme: ThemeId, nextTheme: ThemeId): boolean;
export declare function patchSigmaGlobalGraphAttributes(graph: SigmaGlobalGraphologyGraph, adapterData: GraphRendererAdapterData, theme: ThemeId, edgeStyle?: GraphEdgeStyleOptions): void;
export declare function sigmaGlobalNodeAttributes(node: GraphRendererAdapterNode, communityColorById: Map<string, string>, selectedCommunityIds: ReadonlySet<string> | undefined, theme: ThemeId): SigmaGlobalGraphologyNodeAttributes;
export declare function sigmaSelectedCommunityIds(adapterData: GraphRendererAdapterData): Set<string>;
export declare function sigmaSpotlightCommunityIds(adapterData: GraphRendererAdapterData): Set<string>;
export declare function sigmaSpotlightCommunityId(adapterData: GraphRendererAdapterData): string | null;
export declare function sigmaGlobalNodeSpotlightState(node: GraphRendererAdapterNode, selectedCommunityIds: ReadonlySet<string>): {
    dimmed: boolean;
    forceVisible: boolean;
};
export declare function sigmaGlobalEdgeAttributes(edge: GraphRendererAdapterEdge, theme?: ThemeId, style?: GraphEdgeStyleOptions, selectedCommunityIds?: ReadonlySet<string>): SigmaGlobalGraphologyEdgeAttributes;
export declare function sigmaGlobalEdgeStyle(edge: GraphRendererAdapterEdge, theme?: ThemeId, style?: GraphEdgeStyleOptions, selectedCommunityIds?: ReadonlySet<string>): SigmaGlobalEdgeStyle;
export declare function sigmaGlobalEdgeRelationColor(relationClass: string, theme: ThemeId): string;
export declare function rgbaColor(hexColor: string, alpha: number): string;
export declare function sigmaGlobalCommunityAttributes(community: GraphRendererAdapterCommunity, communityColorById: Map<string, string>): SigmaGlobalGraphologyCommunityAttributes;
export declare function sigmaGlobalAggregationAttributes(aggregation: GraphRendererAdapterAggregation, aggregationRenderById: Map<string, GraphRendererAdapterData["renderable"]["aggregationContainers"][number]>): SigmaGlobalGraphologyAggregationAttributes;
export declare function sigmaGlobalNodeSize(node: GraphRendererAdapterNode): number;
export declare function sigmaGlobalNodeColor(node: GraphRendererAdapterNode, communityColorById: Map<string, string>, theme: ThemeId): string;
export declare function finiteNumber(value: unknown, fallback: number): number;
export declare function clamp(value: number, min: number, max: number): number;
export declare function roundNumber(value: number, digits: number): number;
//# sourceMappingURL=sigma-graphology-model.d.ts.map