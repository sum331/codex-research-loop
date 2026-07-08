import { type GraphSpatialIndex, type GraphSpatialIndexInput } from "../layout";
import type { GraphRendererAdapterData } from "./adapter";
import { type GraphScreenPoint } from "./geometry";
import { type GraphGestureTarget } from "./gestures";
import type { RendererViewport, RendererViewportSize } from "./viewport";
export type SigmaGlobalRenderedObject = {
    kind: "node";
    id: string;
} | {
    kind: "edge";
    id: string;
} | {
    kind: "community-wash";
    id: string;
} | {
    kind: "aggregation-container";
    id: string;
    communityId?: string | null;
};
export interface SigmaGlobalHitInput {
    nodeId?: string | null;
    screenPoint?: GraphScreenPoint | null;
    renderedObject?: SigmaGlobalRenderedObject | null;
    additive?: boolean;
}
export interface SigmaGlobalHitProjectorInput {
    adapterData: GraphRendererAdapterData;
    viewport: RendererViewport;
    viewportSize: RendererViewportSize;
    screenPointToWorldPoint?: (point: GraphScreenPoint) => {
        x: number;
        y: number;
    };
}
export interface SigmaGlobalHitProjector {
    targetFromSigmaHit(input: SigmaGlobalHitInput): GraphGestureTarget;
    index(): GraphSpatialIndex;
}
export declare function createSigmaGlobalHitProjector(input: SigmaGlobalHitProjectorInput): SigmaGlobalHitProjector;
export declare function sigmaNodeIdFromPayload(payload: unknown): string | null;
export declare function sigmaAdditiveFromPayload(payload: unknown): boolean;
export declare function sigmaScreenPointFromPayload(payload: unknown): GraphScreenPoint | null;
export declare function spatialInputFromAdapterData(adapterData: GraphRendererAdapterData): GraphSpatialIndexInput;
export declare function gestureTargetFromSigmaRenderedObject(object: SigmaGlobalRenderedObject, adapterData: GraphRendererAdapterData): GraphGestureTarget | null;
//# sourceMappingURL=sigma-hit-projector.d.ts.map