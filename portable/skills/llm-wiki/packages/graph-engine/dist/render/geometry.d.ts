import type { RendererPoint, RendererViewport, RendererViewportSize } from "./viewport";
export interface GraphWorldPoint {
    x: number;
    y: number;
}
export interface GraphWorldSize {
    width: number;
    height: number;
}
export interface GraphWorldBounds extends GraphWorldSize {
    minX: number;
    minY: number;
    maxX: number;
    maxY: number;
}
export interface GraphScreenPoint {
    x: number;
    y: number;
}
export interface GraphLayerPoint {
    x: number;
    y: number;
}
export interface GraphCssPercentPoint {
    x: number;
    y: number;
}
export interface GraphSvgPoint {
    x: number;
    y: number;
}
export interface GraphMinimapPoint {
    x: number;
    y: number;
}
export interface GraphClientPoint {
    x: number;
    y: number;
}
export interface GraphDomRectLike {
    left: number;
    top: number;
    width: number;
    height: number;
}
export interface GraphWorldRect {
    x: number;
    y: number;
    width: number;
    height: number;
}
export interface GraphMinimapViewBox {
    x: number;
    y: number;
    width: number;
    height: number;
}
export declare const GRAPH_WORLD_SIZE: {
    readonly width: 1000;
    readonly height: 680;
};
export declare const GRAPH_WORLD_BOUNDS: GraphWorldBounds;
export declare const GRAPH_MINIMAP_VIEWBOX: GraphMinimapViewBox;
export declare function rootClientPointToScreenPoint(clientPoint: GraphClientPoint, rootRect: GraphDomRectLike): GraphScreenPoint;
export declare function worldPointToLayerPoint(worldPoint: GraphWorldPoint, viewportSize: RendererViewportSize, worldBounds?: GraphWorldBounds | GraphWorldSize): GraphLayerPoint;
export declare function worldPointToCssPercentPoint(worldPoint: GraphWorldPoint, worldSize?: GraphWorldSize | GraphWorldBounds): GraphCssPercentPoint;
export declare function layerPointToWorldPoint(layerPoint: GraphLayerPoint, viewportSize: RendererViewportSize, worldBounds?: GraphWorldBounds | GraphWorldSize): GraphWorldPoint;
export declare function worldPointToScreenPoint(worldPoint: GraphWorldPoint, viewport: RendererViewport, viewportSize: RendererViewportSize, worldBounds?: GraphWorldBounds | GraphWorldSize): GraphScreenPoint;
export declare function screenPointToWorldPoint(screenPoint: GraphScreenPoint, viewport: RendererViewport, viewportSize: RendererViewportSize, worldBounds?: GraphWorldBounds | GraphWorldSize): GraphWorldPoint;
export declare function worldDeltaToLayerDelta(worldDelta: GraphWorldPoint, viewportSize: RendererViewportSize, worldBounds?: GraphWorldBounds | GraphWorldSize): GraphLayerPoint;
export declare function worldPointDeltaToLayerDelta(previousWorldPoint: GraphWorldPoint, nextWorldPoint: GraphWorldPoint, viewportSize: RendererViewportSize, worldBounds?: GraphWorldBounds | GraphWorldSize): GraphLayerPoint;
export declare function layerDeltaToWorldDelta(layerDelta: GraphLayerPoint, viewportSize: RendererViewportSize, worldBounds?: GraphWorldBounds | GraphWorldSize): GraphWorldPoint;
export declare function worldPointToSvgPoint(worldPoint: GraphWorldPoint): GraphSvgPoint;
export declare function svgPointToWorldPoint(svgPoint: GraphSvgPoint): GraphWorldPoint;
export declare function worldPointToMinimapPoint(worldPoint: GraphWorldPoint, viewBox?: GraphMinimapViewBox, worldBounds?: GraphWorldBounds | GraphWorldSize): GraphMinimapPoint;
export declare function minimapPointToWorldPoint(minimapPoint: GraphMinimapPoint, viewBox?: GraphMinimapViewBox, worldBounds?: GraphWorldBounds | GraphWorldSize): GraphWorldPoint;
export declare function visibleWorldRectForViewport(viewport: RendererViewport, viewportSize: RendererViewportSize, worldBounds?: GraphWorldBounds | GraphWorldSize): GraphWorldRect;
export declare function visibleWorldRectToMinimapRect(worldRect: GraphWorldRect, viewBox?: GraphMinimapViewBox, worldBounds?: GraphWorldBounds | GraphWorldSize): {
    x: number;
    y: number;
    width: number;
    height: number;
};
export declare function rendererPointToScreenPoint(point: RendererPoint): GraphScreenPoint;
export declare function defaultGraphViewportSize(): RendererViewportSize;
export declare function sideExitWorldAnchor(worldPoint: GraphWorldPoint, margin?: number, worldSize?: GraphWorldSize | GraphWorldBounds): GraphWorldPoint;
export declare function worldBoundsForPoints(points: GraphWorldPoint[], options?: {
    padding?: number;
    minWidth?: number;
    minHeight?: number;
    aspectRatio?: number;
}): GraphWorldBounds;
//# sourceMappingURL=geometry.d.ts.map