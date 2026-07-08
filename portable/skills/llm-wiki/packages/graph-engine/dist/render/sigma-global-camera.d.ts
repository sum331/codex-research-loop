import type { GraphRendererAdapterData } from "./adapter";
import type { SigmaGlobalCameraState, SigmaGlobalSigmaLike } from "./sigma-global-types";
export type SigmaGlobalCameraMovement = "animated" | "immediate" | "skipped";
export type SigmaGlobalCameraSkipReason = "no-community" | "already-settled" | "no-target" | "camera-unavailable" | "animate-unavailable" | "animate-error";
export interface SigmaGlobalCameraMoveResult {
    movement: SigmaGlobalCameraMovement;
    skipReason?: SigmaGlobalCameraSkipReason;
}
export interface SigmaCommunitySpotlightCameraResult extends SigmaGlobalCameraMoveResult {
    communityId: string | null;
}
export declare const SIGMA_COMMUNITY_SPOTLIGHT_CAMERA_ANIMATION_MS = 380;
export declare function readCameraState(sigma: SigmaGlobalSigmaLike): SigmaGlobalCameraState | null;
export declare function restoreCameraState(sigma: SigmaGlobalSigmaLike, state: SigmaGlobalCameraState | null): void;
export declare function maybeAnimateSigmaCommunitySpotlightCamera(sigma: SigmaGlobalSigmaLike, root: HTMLElement, adapterData: GraphRendererAdapterData, communityId: string | null, previousCommunityId: string | null, onAnimationError?: (error: unknown) => void): SigmaCommunitySpotlightCameraResult;
export declare function moveSigmaCamera(sigma: SigmaGlobalSigmaLike, target: Partial<SigmaGlobalCameraState>, reducedMotion: boolean, onAnimationError?: (error: unknown) => void): SigmaGlobalCameraMoveResult;
export declare function sigmaCommunitySpotlightCameraState(sigma: SigmaGlobalSigmaLike, adapterData: GraphRendererAdapterData, communityId: string): Partial<SigmaGlobalCameraState> | null;
export declare function sigmaGlobalCameraState(sigma: SigmaGlobalSigmaLike, adapterData: GraphRendererAdapterData): Partial<SigmaGlobalCameraState>;
export declare function sigmaGraphPointToCameraPoint(sigma: SigmaGlobalSigmaLike, point: {
    x: number;
    y: number;
}): {
    x: number;
    y: number;
};
export declare function sigmaCameraDistanceForGraphDistance(sigma: SigmaGlobalSigmaLike, point: {
    x: number;
    y: number;
}, graphDistance: number): number;
export declare function sigmaCommunitySpotlightCenter(adapterData: GraphRendererAdapterData, communityId: string): {
    x: number;
    y: number;
} | null;
export declare function prefersReducedMotion(view: Window | null | undefined): boolean;
//# sourceMappingURL=sigma-global-camera.d.ts.map