import { type GraphSpatialIndex } from "../layout";
import { type GraphScreenPoint } from "./geometry";
import { type GraphGestureTarget } from "./gestures";
import type { RenderableGraph } from "./model";
import type { RendererViewport, RendererViewportSize } from "./viewport";
export interface GraphHitTargetResolverInput {
    graph(): RenderableGraph;
    viewport(): RendererViewport;
    viewportSize(): RendererViewportSize;
}
export interface GraphHitTargetResolver {
    targetFromScreenPoint(screenPoint: GraphScreenPoint): GraphGestureTarget;
    index(): GraphSpatialIndex;
    refresh(): GraphSpatialIndex;
}
export declare function createGraphHitTargetResolver(input: GraphHitTargetResolverInput): GraphHitTargetResolver;
//# sourceMappingURL=hit-testing.d.ts.map