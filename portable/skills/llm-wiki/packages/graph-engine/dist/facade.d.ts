import type { GraphDiff, GraphEdgeStyleOptions, GraphEngine, GraphEngineOptions, GraphData, GraphSummaryObjectRef, GraphVisibilityState, SelectionInput, ThemeId } from "./types";
export { selectionInputForSigmaHit } from "./graph-routes/sigma-global-route";
export type GraphFacadeHostMode = "workbench" | "offline" | "standalone";
export interface GraphFacadeCapabilityContract {
    mode: GraphFacadeHostMode;
    capabilities: GraphEngineOptions["capabilities"];
}
export declare function createGraphWorkbenchCapabilities(capabilities: NonNullable<GraphEngineOptions["capabilities"]>): GraphFacadeCapabilityContract;
export declare function createGraphOfflineCapabilities(capabilities?: Pick<NonNullable<GraphEngineOptions["capabilities"]>, "persistPins">): GraphFacadeCapabilityContract;
export declare function createGraphStandaloneCapabilities(): GraphFacadeCapabilityContract;
export interface GraphFacadeRenderer {
    applyDiff(diff: GraphDiff, options?: {
        reducedMotion?: boolean;
        durationMs?: number;
    }): Promise<void>;
    isDragging(): boolean;
    setData(data: GraphEngineOptions["data"], pins?: GraphEngineOptions["pins"]): void;
    setEdgeStyle(style: GraphEdgeStyleOptions): void;
    setAggregationMarkers(markers: NonNullable<GraphEngineOptions["aggregationMarkers"]>): void;
    focusNode(path: string): void;
    focusCommunity(id: string): void;
    setSourceCommunityContext?(id: string | null): void;
    setTypeFilters(filters: NonNullable<GraphEngineOptions["typeFilters"]>): void;
    showTemporaryObject(object: GraphSummaryObjectRef): void;
    clearTemporaryObjectDisplay(): void;
    resetView(): void;
    select(selection: SelectionInput): void;
    previewNode(id: string | null): void;
    clearSelection(): void;
    clearInteraction(): void;
    setNodeFixed(id: string, mode: "fix" | "unfix"): boolean;
    setTheme(theme: ThemeId): void;
    setPins(pins: NonNullable<GraphEngineOptions["pins"]>): void;
    resetLayout(): void;
    destroy(): void;
}
export type GraphFacadeRendererRouteId = "sigma-global" | "dom-svg-community" | "dom-svg-small-fallback" | "over-limit-notice";
export declare const GRAPH_FACADE_GLOBAL_NODE_LIMIT = 2000;
export declare const GRAPH_FACADE_SIGMA_FALLBACK_THRESHOLDS: {
    readonly maxDomSvgFallbackNodes: 2000;
    readonly maxDomSvgFallbackEdges: 4000;
    readonly maxDomSvgFallbackCommunitySize: 500;
};
export interface GraphFacadeRouteManager extends GraphFacadeRenderer {
    readonly routeId: GraphFacadeRendererRouteId;
    readonly sigmaKnownUnavailable: boolean;
    readonly sigmaAttemptCount: number;
    readonly sourceCommunityId: string | null;
    setSourceCommunityContext(id: string | null): void;
    retrySigma(): void;
}
export interface GraphFacadeRouteRendererOptions {
    data: GraphData;
    pins: NonNullable<GraphEngineOptions["pins"]>;
    theme: ThemeId;
    edgeStyle?: GraphEdgeStyleOptions;
    focus: GraphEngineOptions["focus"];
    typeFilters: NonNullable<GraphEngineOptions["typeFilters"]>;
    aggregationMarkers: NonNullable<GraphEngineOptions["aggregationMarkers"]>;
    selection: SelectionInput | null;
    sourceCommunityId: string | null;
    searchQuery: string;
    searchResultIds: string[];
    temporaryObject: GraphSummaryObjectRef | null;
    callbacks: GraphFacadeRendererCallbacks;
}
export interface GraphFacadeRouteRendererFactoryInput {
    container: HTMLElement;
    options: GraphFacadeRouteRendererOptions;
    onSigmaUnavailable?: (error: unknown) => void;
    onRetrySigma?: () => void;
}
export interface GraphFacadeRouteRendererFactories {
    createSigmaGlobal: (input: GraphFacadeRouteRendererFactoryInput) => GraphFacadeRenderer;
    createDomSvgCommunity: (input: GraphFacadeRouteRendererFactoryInput) => GraphFacadeRenderer;
    createDomSvgSmallFallback: (input: GraphFacadeRouteRendererFactoryInput) => GraphFacadeRenderer;
    createOverLimitNotice: (input: GraphFacadeRouteRendererFactoryInput) => GraphFacadeRenderer;
}
export interface GraphFacadeRendererCallbacks {
    onNodeOpen?: (nodeId: string) => void;
    onSelectionInput?: (selection: SelectionInput) => void;
    onPinsChanged?: (pins: NonNullable<GraphEngineOptions["pins"]>) => void;
    onSelectionClearRequested?: () => void;
    onViewReset?: () => void;
    onGlobalResetRequested?: () => void;
    onDragActiveChange?: (dragging: boolean) => void;
    onVisibilityStateChange?: (state: GraphVisibilityState) => void;
}
interface GraphFacadeContainer {
    dataset: Record<string, string | undefined>;
}
export interface GraphFacadeState {
    data: GraphData;
    pins: NonNullable<GraphEngineOptions["pins"]>;
    theme?: ThemeId;
    edgeStyle?: GraphEdgeStyleOptions;
    focus?: GraphEngineOptions["focus"];
    typeFilters?: NonNullable<GraphEngineOptions["typeFilters"]>;
    aggregationMarkers?: NonNullable<GraphEngineOptions["aggregationMarkers"]>;
    selection?: SelectionInput | null;
    sourceCommunityId?: string | null;
    searchQuery?: string;
    searchResultIds?: string[];
    temporaryObject?: GraphSummaryObjectRef | null;
}
export declare function createGraphFacade(container: HTMLElement, options: GraphEngineOptions): GraphEngine;
export declare function createGraphFacadeRouteManager(container: HTMLElement, options: {
    state: GraphFacadeState;
    toolbarContainer?: HTMLElement | null;
    callbacks?: GraphFacadeRendererCallbacks;
    factories?: Partial<GraphFacadeRouteRendererFactories>;
}): GraphFacadeRouteManager;
export declare function graphExceedsGlobalNodeLimit(data: GraphData): boolean;
export declare function graphRequiresAggregationSafetyFallback(data: GraphData): boolean;
export declare function createGraphFacadeFromRenderer(container: GraphFacadeContainer, renderer: GraphFacadeRenderer, options: GraphEngineOptions, facadeState?: GraphFacadeState): GraphEngine;
//# sourceMappingURL=facade.d.ts.map