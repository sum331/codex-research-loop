import type { GraphScreenPoint, GraphWorldBounds, GraphWorldPoint } from "./geometry";
import type { RendererViewport, RendererViewportSize } from "./viewport";
export interface GraphNodeDragStartInput {
    nodeWorldPoint: GraphWorldPoint;
    pointerScreenPoint: GraphScreenPoint;
    viewport: RendererViewport;
    viewportSize: RendererViewportSize;
    worldBounds?: GraphWorldBounds;
}
export interface GraphNodeDragMoveInput {
    pointerScreenPoint: GraphScreenPoint;
    viewport: RendererViewport;
    viewportSize: RendererViewportSize;
    worldBounds?: GraphWorldBounds;
    grabOffset: GraphWorldPoint;
}
export interface GraphNodeDragStartState {
    pointerWorldPoint: GraphWorldPoint;
    grabOffset: GraphWorldPoint;
    targetWorldPoint: GraphWorldPoint;
}
export declare function beginGraphNodeDrag(input: GraphNodeDragStartInput): GraphNodeDragStartState;
export declare function resolveGraphNodeDragTarget(input: GraphNodeDragMoveInput): GraphWorldPoint;
//# sourceMappingURL=simulation-bridge.d.ts.map