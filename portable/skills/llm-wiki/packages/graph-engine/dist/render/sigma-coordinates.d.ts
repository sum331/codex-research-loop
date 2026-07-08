import { type GraphScreenPoint } from "./geometry";
import type { SigmaGlobalCameraState, SigmaGlobalRendererCreateOptions, SigmaGlobalSigmaLike } from "./sigma-global-types";
export declare function overlayPointerScreenPoint(event: MouseEvent | PointerEvent, root: HTMLElement): GraphScreenPoint;
export declare function sigmaScreenPointToWorldPoint(sigma: SigmaGlobalSigmaLike, point: GraphScreenPoint, options: Pick<SigmaGlobalRendererCreateOptions, "viewport" | "viewportSize" | "adapterData">): {
    x: number;
    y: number;
};
export declare function sigmaWorldPointToScreenPoint(sigma: SigmaGlobalSigmaLike, point: {
    x: number;
    y: number;
}, options: Pick<SigmaGlobalRendererCreateOptions, "viewport" | "viewportSize" | "adapterData">): GraphScreenPoint;
export declare function sigmaWorldPointToScreenPointForCameraState(sigma: SigmaGlobalSigmaLike, point: {
    x: number;
    y: number;
}, cameraState: SigmaGlobalCameraState, options: Pick<SigmaGlobalRendererCreateOptions, "viewport" | "viewportSize" | "adapterData">): GraphScreenPoint;
//# sourceMappingURL=sigma-coordinates.d.ts.map