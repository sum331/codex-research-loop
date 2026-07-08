import type { GraphRendererAdapterData, GraphRendererAdapterNode } from "./adapter";
import type { SigmaCommunityCloud } from "./community-cloud-geometry";
import type { GraphScreenPoint } from "./geometry";
import type { SigmaGlobalRendererCreateOptions, SigmaGlobalSigmaLike } from "./sigma-global-types";
import type { SigmaGlobalRenderedObject } from "./sigma-hit-projector";
export interface SigmaOverlayDomController {
    rebuild(): void;
    reposition(): void;
    repositionForCameraAnimation(): boolean;
    invalidateAnimationBaseline(): void;
    clearActiveDragListeners(): void;
    destroy(): void;
}
export interface SigmaOverlayDomControllerInput {
    overlayRoot: HTMLElement;
    cloudFilterId: string;
    getAdapterData: () => GraphRendererAdapterData;
    getSigma: () => SigmaGlobalSigmaLike;
    getOptions: () => Pick<SigmaGlobalRendererCreateOptions, "viewport" | "viewportSize" | "adapterData">;
    communityCloudFor: (communityId: string, wash: {
        cx: number;
        cy: number;
        rx: number;
        ry: number;
    }) => SigmaCommunityCloud;
    isDestroyed: () => boolean;
    onHit: (object: SigmaGlobalRenderedObject) => void;
    beginNodeDrag: (nodeId: string, point: GraphScreenPoint, payload?: unknown) => void;
    moveNodeDrag: (point: GraphScreenPoint, payload?: unknown) => void;
    commitNodeDrag: (point: GraphScreenPoint | null, payload?: unknown) => void;
    cancelNodeDrag: () => void;
    screenPointFromEvent: (event: MouseEvent | PointerEvent) => GraphScreenPoint;
    consumeSuppressedNodeClick: (nodeId: string | null) => boolean;
    activeNodeDragId: () => string | null;
}
export declare function createSigmaOverlayDomController(input: SigmaOverlayDomControllerInput): SigmaOverlayDomController;
export declare function sigmaOverlayNodes(adapterData: GraphRendererAdapterData): GraphRendererAdapterNode[];
export declare function sigmaCommunityLabels(adapterData: GraphRendererAdapterData, limit: number): GraphRendererAdapterData["renderable"]["communities"];
//# sourceMappingURL=sigma-overlay-dom.d.ts.map