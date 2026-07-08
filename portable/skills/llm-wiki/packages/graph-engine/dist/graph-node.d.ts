import type { GraphNodeType, WikiPath } from "./types";
interface GraphNodePathInput {
    id: string;
    type?: unknown;
    source_path?: unknown;
    path?: unknown;
    source?: unknown;
}
export declare function wikiPathForGraphNode(node: GraphNodePathInput): WikiPath;
export declare function wikiDirectoryForGraphNodeType(type: unknown): string;
export declare function graphNodeTypeLabel(type: GraphNodeType | unknown): string;
export {};
//# sourceMappingURL=graph-node.d.ts.map