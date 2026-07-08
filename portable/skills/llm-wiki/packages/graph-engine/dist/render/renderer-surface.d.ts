import type { NodeId } from "../types";
import type { PaintedGraphDom } from "./render-context";
import type { GraphSearchNodeView } from "./search";
export interface GraphRendererSurface {
    focusRoot(options?: FocusOptions): void;
    focusNode(id: NodeId, options?: FocusOptions): void;
    setNodeDragging(id: NodeId, dragging: boolean): void;
    clearNodeDragging(): void;
    setViewportDragging(dragging: boolean): void;
    setDragTarget(id: NodeId | null): void;
    setFocusDataset(active: boolean): void;
    setSearchOpen(open: boolean): void;
    setSearchState(input: {
        query: string;
        focusedNodeId: NodeId | null;
        nodes: readonly GraphSearchNodeView[];
    }): void;
}
export declare function createDomSvgRendererSurface(input: {
    root: HTMLElement;
    dom: () => PaintedGraphDom;
}): GraphRendererSurface;
//# sourceMappingURL=renderer-surface.d.ts.map