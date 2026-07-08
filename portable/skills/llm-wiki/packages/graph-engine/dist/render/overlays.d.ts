import { type GraphScreenPoint, type GraphWorldBounds, type GraphWorldPoint } from "./geometry";
import type { RendererViewport, RendererViewportSize } from "./viewport";
export interface GraphOverlayNodeLike {
    point: GraphWorldPoint;
}
export interface GraphOverlayEdgeLike {
    source?: GraphOverlayNodeLike | null;
    target?: GraphOverlayNodeLike | null;
}
export interface GraphPreviewSize {
    width: number;
    height: number;
}
export interface GraphPreviewPositionInput {
    anchorScreenPoint: GraphScreenPoint;
    previewSize: GraphPreviewSize;
    viewportSize: RendererViewportSize;
    offset: {
        x: number;
        y: number;
    };
    margin?: number;
}
export declare function graphNodeHoverAnchor(node: GraphOverlayNodeLike, viewport: RendererViewport, viewportSize: RendererViewportSize, worldBounds?: GraphWorldBounds): GraphScreenPoint;
export declare function graphEdgeHoverAnchor(edge: GraphOverlayEdgeLike, viewport: RendererViewport, viewportSize: RendererViewportSize, worldBounds?: GraphWorldBounds): GraphScreenPoint;
export declare function resolveGraphHoverPreviewPosition(input: GraphPreviewPositionInput): GraphScreenPoint;
//# sourceMappingURL=overlays.d.ts.map