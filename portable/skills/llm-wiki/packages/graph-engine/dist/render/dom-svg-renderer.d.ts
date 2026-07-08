import type { NodeId, ThemeId } from "../types";
import { type GraphAggregationContainerElementHandlers } from "./aggregation-containers";
import { type GraphEdgeElementHandlers } from "./edges";
import type { RenderableGraph } from "./model";
import { type GraphNodeElementHandlers } from "./nodes";
import type { PaintedGraphDom } from "./render-context";
export interface DomSvgGraphPaintHandlers extends GraphNodeElementHandlers, GraphEdgeElementHandlers, GraphAggregationContainerElementHandlers {
    onNodeClick: (id: NodeId, additive: boolean) => void;
    onNodeDoubleClick: (id: string) => boolean;
    onNodePreviewEnter: (id: NodeId) => void;
    onEdgePreviewEnter: (id: string) => void;
    onEdgePreviewLeave: () => void;
    onNodePreviewLeave: () => void;
}
export interface PaintDomSvgGraphInput {
    ownerDocument: Document;
    root: HTMLElement;
    graph: RenderableGraph;
    theme: ThemeId;
    hasHostReader: boolean;
    handlers: DomSvgGraphPaintHandlers;
}
export declare function paintDomSvgGraph(input: PaintDomSvgGraphInput): PaintedGraphDom;
//# sourceMappingURL=dom-svg-renderer.d.ts.map