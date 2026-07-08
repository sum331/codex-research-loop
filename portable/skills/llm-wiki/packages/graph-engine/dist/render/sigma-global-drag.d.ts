import type { PinPosition } from "../types";
import type { GraphRendererAdapterData } from "./adapter";
import type { GraphScreenPoint } from "./geometry";
export declare const SIGMA_GLOBAL_NODE_DRAG_START_THRESHOLD = 2;
export interface SigmaGlobalNodeDragSession {
    nodeId: string;
    pinKey: string;
    startPoint: {
        x: number;
        y: number;
    };
    currentPoint: {
        x: number;
        y: number;
    };
    initiallyPinned: boolean;
    initialPinPosition: PinPosition | null;
    pointerStart: GraphScreenPoint;
    grabOffset: {
        x: number;
        y: number;
    };
    previousCameraPanning: unknown;
    moved: boolean;
}
export declare function createSigmaGlobalNodeDragSession(input: {
    nodeId: string;
    pinKey: string;
    startPoint: {
        x: number;
        y: number;
    };
    pointerStart: GraphScreenPoint;
    pointerWorldPoint: {
        x: number;
        y: number;
    };
    initiallyPinned: boolean;
    initialPinPosition: PinPosition | null;
    previousCameraPanning: unknown;
}): SigmaGlobalNodeDragSession;
export declare function moveSigmaGlobalNodeDragSession(drag: SigmaGlobalNodeDragSession, screenPoint: GraphScreenPoint, pointerWorldPoint: {
    x: number;
    y: number;
}): void;
export declare function sigmaAdapterDataWithNodePoint(adapterData: GraphRendererAdapterData, nodeId: string, point: {
    x: number;
    y: number;
}, pinned: boolean, pinPosition: PinPosition | null): GraphRendererAdapterData;
export declare function bindSigmaGlobalOverlayPointerDrag(input: {
    ownerDocument: Document;
    element: HTMLElement;
    nodeId: string;
    pointerId: number;
    isActive: (nodeId: string) => boolean;
    screenPointFromEvent: (event: PointerEvent) => GraphScreenPoint;
    onMove: (point: GraphScreenPoint, event: PointerEvent) => void;
    onEnd: (point: GraphScreenPoint, event: PointerEvent) => void;
    onCancel: () => void;
}): () => void;
export declare function bindSigmaGlobalOverlayMouseDrag(input: {
    ownerDocument: Document;
    nodeId: string;
    isActive: (nodeId: string) => boolean;
    screenPointFromEvent: (event: MouseEvent) => GraphScreenPoint;
    onMove: (point: GraphScreenPoint, event: MouseEvent) => void;
    onEnd: (point: GraphScreenPoint, event: MouseEvent) => void;
}): () => void;
//# sourceMappingURL=sigma-global-drag.d.ts.map