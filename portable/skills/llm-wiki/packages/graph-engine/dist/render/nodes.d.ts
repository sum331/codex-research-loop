import type { NodeId } from "../types";
import type { NodeDisplayMode, RenderableNode } from "./model";
export interface GraphNodeElementHandlers {
    onNodeClick: (id: NodeId, additive: boolean) => void;
    onNodeDoubleClick: (id: NodeId) => boolean;
    onNodePreviewEnter: (id: NodeId) => void;
    onNodePreviewLeave: () => void;
}
export interface GraphNodeElementOptions {
    communityMap?: boolean;
}
export declare function createGraphNodeElement(ownerDocument: Document, node: RenderableNode, handlers: GraphNodeElementHandlers, options?: GraphNodeElementOptions): HTMLButtonElement;
export declare function applyGraphNodeDisplayMode(button: HTMLButtonElement, displayMode: NodeDisplayMode): void;
//# sourceMappingURL=nodes.d.ts.map