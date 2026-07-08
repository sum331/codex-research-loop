import type { CommunityId, GraphAggregationMarker, GraphFocusInput, GraphSummaryObjectRef, GraphTypeFilters, GraphData, GraphDiff, NodeId, PinMap, SelectionInput, ThemeId, WikiPath } from "../types";
import { type RenderableGraph } from "./model";
import type { GraphRendererCallbacks } from "./render-context";
export interface GraphRendererOptions {
    data: GraphData;
    pins?: PinMap;
    theme: ThemeId;
    onNodeOpen?: (nodeId: NodeId) => void;
    onSelectionInput?: (selection: SelectionInput) => void;
    onSelectionClearRequested?: () => void;
    onViewReset?: () => void;
    onGlobalResetRequested?: () => void;
    onPinsChanged?: (pins: PinMap) => void;
    onDragActiveChange?: (dragging: boolean) => void;
    onVisibilityStateChange?: GraphRendererCallbacks["onVisibilityStateChange"];
    toolbarContainer?: HTMLElement | null;
    focus?: GraphFocusInput;
    typeFilters?: GraphTypeFilters;
    aggregationMarkers?: GraphAggregationMarker[];
    searchQuery?: string;
    live?: boolean;
    sourceCommunityId?: string | null;
}
type RenderNextOptions = Partial<GraphRendererOptions> & {
    selectedNodeId?: string | null;
    selection?: SelectionInput | null;
};
export interface GraphRenderer {
    root: HTMLElement;
    graph: RenderableGraph;
    render(next?: RenderNextOptions): void;
    applyDiff(diff: GraphDiff, options?: {
        reducedMotion?: boolean;
        durationMs?: number;
    }): Promise<void>;
    isDragging(): boolean;
    setData(data: GraphData, pins?: PinMap): void;
    setAggregationMarkers(markers: GraphAggregationMarker[]): void;
    setTheme(theme: ThemeId): void;
    setPins(pins: PinMap): void;
    focusNode(pathOrId: WikiPath): void;
    focusCommunity(id: CommunityId): void;
    setSourceCommunityContext(id: CommunityId | null): void;
    setTypeFilters(filters: GraphTypeFilters): void;
    showTemporaryObject(object: GraphSummaryObjectRef): void;
    clearTemporaryObjectDisplay(): void;
    resetView(): void;
    select(selection: SelectionInput): void;
    previewNode(id: NodeId | null): void;
    clearSelection(): void;
    clearInteraction(): void;
    resetLayout(): void;
    setNodeFixed(id: NodeId, mode: "fix" | "unfix"): boolean;
    destroy(): void;
}
export declare function createGraphRenderer(container: HTMLElement, options: GraphRendererOptions): GraphRenderer;
export {};
//# sourceMappingURL=graph-renderer-root.d.ts.map