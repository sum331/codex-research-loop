import type { GraphDiff, GraphSummaryObjectRef, NodeId } from "../types";
import { type DomSvgGraphPaintHandlers } from "./dom-svg-renderer";
import { type RenderableGraph, type RenderPositionMap } from "./model";
import { type RendererViewport, type ViewportFrameCommitOptions } from "./viewport";
import type { GraphRenderContext, PaintedGraphDom } from "./render-context";
type PaintHandlers = DomSvgGraphPaintHandlers;
export interface GraphRenderCommands {
    render(next?: {
        typeFilters?: Record<string, boolean>;
    }): void;
    resetViewState(): void;
    requestGlobalReset(): void;
    openSearch(): void;
    applySearchQuery(query: string): void;
    focusNextSearchResult(): void;
    focusPreviousSearchResult(): void;
    activateSearchResult(): void;
    closeSearch(): void;
    selectCommunity(id: string): void;
    setCommunityHover(id: string | null): void;
    selectAggregationContainer(id: string | null): void;
    handleNodeClick(id: NodeId, additive: boolean): void;
    handleNodeDoubleClick(id: string): boolean;
    setNodeFixed(id: string, mode: "fix" | "unfix"): boolean;
    setNodeHover(id: NodeId | null): void;
    scheduleHoverPreview(id: NodeId): void;
    showEdgeHoverPreview(id: string): void;
    clearHoverPreview(): void;
    cancelHoverPreviewOnly(): void;
}
export interface GraphRenderOverlayDelegates {
    renderReader(): void;
    renderSelectionPanel(): void;
    renderHoverPreview(): void;
}
export interface GraphRenderPipeline {
    rebuildAndPaint(): void;
    paint(graph: RenderableGraph, options: {
        hasHostReader: boolean;
        handlers: PaintHandlers;
    }): PaintedGraphDom;
    mountSearchControl(): void;
    mountGraphToolbar(): void;
    mountCommunityLegend(): void;
    applyTypeFilters(filters: Record<string, boolean>): void;
    showTemporaryObject(object: GraphSummaryObjectRef): void;
    clearTemporaryObjectDisplay(): void;
    applyCommunityHover(): void;
    applyRelationFocus(): void;
    bindResizeObserver(): void;
    commitViewport(nextViewport: RendererViewport, options?: ViewportFrameCommitOptions): void;
    resetRootScroll(): void;
    updateEffectiveDensity(): void;
    renderMotionOverlays(): void;
    updateMinimapViewport(): void;
    setViewportAnimating(enabled: boolean): void;
    setInteractionDegraded(enabled: boolean, options?: {
        restoreDelayMs?: number;
    }): void;
    viewportSize(): {
        width: number;
        height: number;
    };
    restartSimulation(): void;
    applyMotionFrame(positions: RenderPositionMap): void;
    markPinnedNodes(pinnedNodeIds: string[]): void;
    animateDiff(diff: GraphDiff, options?: {
        reducedMotion?: boolean;
        durationMs?: number;
    }): Promise<void>;
    markDiffElements(diff: GraphDiff): void;
    settleDiffElements(): void;
    semanticAnchorForNode(id: NodeId): {
        x: number;
        y: number;
    } | null;
    destroy(): void;
}
export interface GraphRenderPipelineOptions {
    commands: GraphRenderCommands;
    overlays: GraphRenderOverlayDelegates;
    hasHostReader: boolean;
    live: boolean;
}
export declare function shouldRunLiveSimulation(graph: Pick<RenderableGraph, "focus" | "nodes">, live: boolean): boolean;
export declare function createGraphRenderPipeline(context: GraphRenderContext, options: GraphRenderPipelineOptions): GraphRenderPipeline;
export declare function positionsFromRenderableGraph(graph: RenderableGraph): RenderPositionMap;
export declare function initialViewportSize(root: HTMLElement): {
    width: number;
    height: number;
};
export declare function emptyPaintedDom(): PaintedGraphDom;
export declare function readLegendCollapsed(ownerDocument: Document): boolean;
export declare function round(value: number): number;
export {};
//# sourceMappingURL=render-pipeline.d.ts.map