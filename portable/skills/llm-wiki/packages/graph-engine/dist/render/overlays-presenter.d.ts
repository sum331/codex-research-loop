import type { NodeId } from "../types";
import type { GraphRuntimeStateSnapshot } from "./state";
import type { GraphRenderContext } from "./render-context";
export interface GraphOverlaysPresenter {
    scheduleHoverPreview(id: NodeId): void;
    showEdgeHoverPreview(id: string): void;
    clearHoverPreview(): void;
    cancelHoverPreviewOnly(): void;
    setGraphHover(hover: GraphRuntimeStateSnapshot["hover"]): GraphRuntimeStateSnapshot;
    renderHoverPreview(): void;
    renderReader(): void;
    renderSelectionPanel(): void;
    destroy(): void;
}
export interface GraphOverlaysPresenterOptions {
    viewportSize(): {
        width: number;
        height: number;
    };
    clearInteractionState(): void;
}
export declare function createGraphOverlaysPresenter(context: GraphRenderContext, options: GraphOverlaysPresenterOptions): GraphOverlaysPresenter;
//# sourceMappingURL=overlays-presenter.d.ts.map