import type { RenderableEdge } from "./model";
export interface GraphEdgeElementHandlers {
    onEdgePreviewEnter: (id: string) => void;
    onEdgePreviewLeave: () => void;
}
export declare function createGraphEdgeElement(ownerDocument: Document, edge: RenderableEdge, handlers: GraphEdgeElementHandlers): SVGPathElement;
export declare function edgeConfidenceLabel(confidence: string): string;
//# sourceMappingURL=edges.d.ts.map