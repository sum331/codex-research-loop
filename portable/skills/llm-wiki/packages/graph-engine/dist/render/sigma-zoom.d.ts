export interface SigmaWheelDeltaLike {
    deltaY: number;
    deltaMode?: number;
}
export type SigmaButtonZoomDirection = "in" | "out";
export declare const SIGMA_WHEEL_LINE_HEIGHT_PX = 18;
export declare const SIGMA_WHEEL_PAGE_HEIGHT_PX = 720;
export declare const SIGMA_WHEEL_ZOOM_SPEED = 0.0016;
export declare const SIGMA_WHEEL_ZOOM_FACTOR_MIN = 0.2;
export declare const SIGMA_WHEEL_ZOOM_FACTOR_MAX = 5;
export declare const SIGMA_CAMERA_MIN_RATIO = 0.3;
export declare const SIGMA_CAMERA_MAX_RATIO = 3;
export declare const SIGMA_BUTTON_ZOOM_RATIO = 1.18;
export declare const SIGMA_BUTTON_ZOOM_DURATION_MS = 140;
export declare function normalizeSigmaWheelDelta(delta: SigmaWheelDeltaLike): number;
export declare function sigmaWheelZoomRatio(currentRatio: number, delta: SigmaWheelDeltaLike): number;
export declare function sigmaButtonZoomRatio(currentRatio: number, direction: SigmaButtonZoomDirection): number;
//# sourceMappingURL=sigma-zoom.d.ts.map