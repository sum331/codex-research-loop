import type { GraphNode } from "../types";
export interface GraphHoverPreview {
    id: string;
    title: string;
    typeLabel: string;
    summary: string;
}
export declare function buildHoverPreview(node: Pick<GraphNode, "id" | "label" | "type" | "content" | "summary">): GraphHoverPreview;
export declare function previewSummary(node: Pick<GraphNode, "content" | "summary">): string;
export declare function firstUsefulParagraph(markdown: string): string;
//# sourceMappingURL=preview.d.ts.map