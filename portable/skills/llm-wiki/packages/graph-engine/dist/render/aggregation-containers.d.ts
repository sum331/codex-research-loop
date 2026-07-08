import type { RenderableAggregationContainer } from "./model";
export interface GraphAggregationContainerElementHandlers {
    onAggregationContainerClick: (container: RenderableAggregationContainer) => void;
}
export declare function createGraphAggregationContainerElement(ownerDocument: Document, container: RenderableAggregationContainer, handlers: GraphAggregationContainerElementHandlers): HTMLButtonElement;
//# sourceMappingURL=aggregation-containers.d.ts.map