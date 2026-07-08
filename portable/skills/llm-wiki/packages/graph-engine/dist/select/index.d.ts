import type { GraphData, NodeId, Selection, SelectionAction, SelectionActionId, SelectionFacts, SelectionInput } from "../types";
export type PageReaderActionId = "quote_page" | "find_related_pages";
export interface PageReaderAction {
    id: PageReaderActionId;
    label: string;
}
export declare function pageSelectionActions(isolated?: boolean): SelectionAction[];
export declare function pageReaderActions(): PageReaderAction[];
export declare function resolveSelection(data: GraphData, input: SelectionInput): Selection;
export declare function toggleNodeInSelection(data: GraphData, current: SelectionInput | null | undefined, nodeId: NodeId): SelectionInput | null;
export declare function resolveSelectionForCapabilities(data: GraphData, input: SelectionInput, capabilities: {
    canAsk?: boolean;
}): Selection;
export declare function selectionActions(facts: SelectionFacts, input?: SelectionInput): SelectionAction[];
export declare function groupDrawerActions(): SelectionAction[];
export declare function groupDrawerActionById(id: string | null): SelectionAction | null;
export declare function recommendedGroupActionForCommunity(state: "clear" | "loose" | "ungrouped"): SelectionActionId;
export declare function recommendedGroupActionForSelection(facts: SelectionFacts): SelectionActionId;
//# sourceMappingURL=index.d.ts.map