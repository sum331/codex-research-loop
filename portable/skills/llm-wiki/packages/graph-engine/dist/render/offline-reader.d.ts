import type { GraphNode, SelectionInput } from "../types";
export interface OfflineReaderNode {
    id: string;
    label: string;
    type: string;
    content?: string;
    summary?: string;
}
export interface OfflineSelectionPanelInput {
    selection: SelectionInput | null;
    selectedNodes: GraphNode[];
    facts: {
        pageCount: number;
        internalLinkCount: number;
        communityCount: number;
        isolatedCount: number;
    } | null;
}
export declare function renderOfflineReader(ownerDocument: Document, reader: HTMLElement, input: {
    selected: OfflineReaderNode | null;
    rawNode: GraphNode | null;
    onClose: () => void;
}): void;
export declare function renderOfflineSelectionPanel(ownerDocument: Document, panel: HTMLElement, input: OfflineSelectionPanelInput & {
    onClose: () => void;
}): void;
//# sourceMappingURL=offline-reader.d.ts.map