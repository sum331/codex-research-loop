import type { GraphData, SelectionInput } from "../types";
import { type GraphGestureTarget } from "../render";
import type { SigmaGlobalHitContext } from "../render/sigma-global-types";
import type { GraphFacadeRenderer, GraphFacadeRouteRendererFactoryInput } from "../facade";
export declare function selectionInputForSigmaHit(data: GraphData, current: SelectionInput | null | undefined, target: GraphGestureTarget, context: SigmaGlobalHitContext): SelectionInput | null;
export declare function createSigmaGlobalFacadeRenderer(input: GraphFacadeRouteRendererFactoryInput): GraphFacadeRenderer;
//# sourceMappingURL=sigma-global-route.d.ts.map