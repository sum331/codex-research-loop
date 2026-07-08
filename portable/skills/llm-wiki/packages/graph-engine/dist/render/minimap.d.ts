import type { RenderableMinimap } from "./model";
export interface GraphMinimapDom {
    element: HTMLElement;
    nodeElements: Map<string, SVGCircleElement>;
    viewportElement: SVGRectElement;
}
export declare function createGraphMinimap(ownerDocument: Document, minimap: RenderableMinimap): GraphMinimapDom;
//# sourceMappingURL=minimap.d.ts.map