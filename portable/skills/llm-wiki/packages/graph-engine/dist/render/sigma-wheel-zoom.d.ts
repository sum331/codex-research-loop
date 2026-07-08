import type { GraphScreenPoint } from "./geometry";
import type { SigmaGlobalSigmaLike } from "./sigma-global-types";
import { type SigmaWheelDeltaLike } from "./sigma-zoom";
export interface SigmaWheelZoomController {
    destroy(): void;
}
export interface SigmaWheelZoomControllerInput {
    sigma: SigmaGlobalSigmaLike;
    root: HTMLElement;
    isDestroyed: () => boolean;
    currentRatio: () => number;
    onZoomAtPoint: (point: GraphScreenPoint, nextRatio: number) => void;
    onFatalError?: (error: unknown) => void;
}
export declare function bindSigmaWheelZoomController(input: SigmaWheelZoomControllerInput): SigmaWheelZoomController;
export declare function sigmaWheelInputFromPayload(payload: unknown, fallbackPoint: GraphScreenPoint): {
    point: GraphScreenPoint;
    delta: SigmaWheelDeltaLike;
} | null;
export declare function sigmaWheelTargetIsZoomControl(payload: unknown): boolean;
export declare function sigmaViewportCenter(root: HTMLElement): GraphScreenPoint;
//# sourceMappingURL=sigma-wheel-zoom.d.ts.map