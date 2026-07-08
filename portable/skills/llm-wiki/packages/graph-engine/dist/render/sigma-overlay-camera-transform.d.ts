import type { GraphScreenPoint } from "./geometry";
export interface SigmaOverlayCameraAnchorProjection {
    center: GraphScreenPoint;
    right: GraphScreenPoint;
    down: GraphScreenPoint;
}
export interface SigmaOverlayCameraAnchorWorldPoints {
    center: {
        x: number;
        y: number;
    };
    right: {
        x: number;
        y: number;
    };
    down: {
        x: number;
        y: number;
    };
}
export interface SigmaOverlayCameraTransform {
    translateX: number;
    translateY: number;
    scale: number;
}
export declare function sigmaOverlayCameraAnchorWorldPoints(bounds: {
    minX: number;
    maxX: number;
    minY: number;
    maxY: number;
}): SigmaOverlayCameraAnchorWorldPoints;
export declare function projectSigmaOverlayCameraAnchors(anchors: SigmaOverlayCameraAnchorWorldPoints, project: (point: {
    x: number;
    y: number;
}) => GraphScreenPoint): SigmaOverlayCameraAnchorProjection;
export declare function sigmaOverlayCameraTransform(baseline: SigmaOverlayCameraAnchorProjection, current: SigmaOverlayCameraAnchorProjection): SigmaOverlayCameraTransform | null;
export declare function sigmaOverlayCameraTransformCss(transform: SigmaOverlayCameraTransform | null): string;
//# sourceMappingURL=sigma-overlay-camera-transform.d.ts.map