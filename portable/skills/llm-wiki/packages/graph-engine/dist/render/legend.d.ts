import type { NodeId } from "../types";
import type { RenderableCommunity, RenderableNode } from "./model";
export interface CommunityLegendRow {
    id: string;
    label: string;
    color: string;
    pageCount: number;
    nodeIds: NodeId[];
}
export declare function buildCommunityLegend(communities: Array<Pick<RenderableCommunity, "id" | "label" | "color" | "nodeCount" | "wash">>, nodes: Array<Pick<RenderableNode, "id" | "community">>): CommunityLegendRow[];
//# sourceMappingURL=legend.d.ts.map