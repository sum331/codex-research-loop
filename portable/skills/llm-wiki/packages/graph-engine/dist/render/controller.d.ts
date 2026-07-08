import type { CommunityId, NodeId } from "../types";
import { GraphGestureController, type GraphGestureIntent } from "./gestures";
import type { RenderPositionMap } from "./model";
import type { GraphRenderContext } from "./render-context";
import type { GraphRuntimeStateSnapshot } from "./state";
import { type RendererViewportSize } from "./viewport";
export interface GraphController {
    bindViewportHandlers(): GraphGestureController;
    onGestureIntents(intents: GraphGestureIntent[], event: PointerEvent | null): void;
    syncRuntimeGestureState(): void;
    handleDocumentKeydown(event: KeyboardEvent): void;
    isGraphKeyboardFocusActive(): boolean;
    handleNodeClick(id: NodeId, additive: boolean): void;
    handleNodeDoubleClick(id: NodeId): boolean;
    setNodeFixed(id: NodeId, mode: "fix" | "unfix"): boolean;
    handleBlankClick(): void;
    openSearch(): void;
    applySearchQuery(query: string): void;
    focusNextSearchResult(): void;
    focusPreviousSearchResult(): void;
    activateSearchResult(): void;
    closeSearch(): void;
    selectCommunity(id: CommunityId): void;
    setCommunityHover(id: CommunityId | null): void;
    focusCommunity(id: CommunityId): void;
    resetViewState(): void;
    requestGlobalReset(): void;
    retreatFocusedView(): void;
    clearSelectionOnly(): void;
    closeToolbarPanel(): void;
    clearInteractionState(): void;
    clearTransientInteractionForDataRefresh(): void;
    hasInteractionState(): boolean;
}
export interface GraphControllerDelegates {
    render(): void;
    viewportSize(): RendererViewportSize;
    setViewportAnimating(enabled: boolean): void;
    setInteractionDegraded(enabled: boolean, options?: {
        restoreDelayMs?: number;
    }): void;
    setGraphHover(hover: GraphRuntimeStateSnapshot["hover"]): GraphRuntimeStateSnapshot;
    applyMotionFrame(positions: RenderPositionMap): void;
    markPinnedNodes(pinnedNodeIds: string[]): void;
    focusFitMaxScale: number;
}
export declare function createGraphController(context: GraphRenderContext, delegates: GraphControllerDelegates): GraphController;
//# sourceMappingURL=controller.d.ts.map