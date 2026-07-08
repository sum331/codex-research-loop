import type { GraphTypeFilters } from "../types";
import type { CommunityLegendRow } from "./legend";
import type { GraphToolbarPanelState } from "./toolbar";
export interface GraphToolbarDom {
    element: HTMLElement;
    panel: HTMLElement;
    filtersPanel: HTMLElement;
    buttons: {
        filters: HTMLButtonElement;
        legend: HTMLButtonElement;
    };
}
export interface CommunityLegendDom {
    element: HTMLElement;
    rows: Map<string, HTMLButtonElement>;
}
export interface SearchControlDom {
    element: HTMLElement;
    input: HTMLInputElement;
    status: HTMLElement;
}
export interface SigmaZoomControlsDom {
    element: HTMLElement;
    buttons: {
        zoomIn: HTMLButtonElement;
        zoomOut: HTMLButtonElement;
    };
}
export declare function createGraphToolbar(ownerDocument: Document, options: {
    panelState: GraphToolbarPanelState;
    typeFilters: GraphTypeFilters;
    onPanelToggle: (panel: Exclude<GraphToolbarPanelState, "closed">) => void;
    onTypeFilterToggle: (type: string, enabled: boolean) => void;
    onReset: () => void;
}): GraphToolbarDom;
export declare function createSigmaZoomControls(ownerDocument: Document, options: {
    onZoomIn: () => void;
    onZoomOut: () => void;
}): SigmaZoomControlsDom;
export declare function createCommunityLegend(ownerDocument: Document, options: {
    rows: CommunityLegendRow[];
    collapsed: boolean;
    onToggle: () => void;
    onHover: (id: string | null) => void;
    onSelect: (id: string) => void;
}): CommunityLegendDom;
export declare function createSearchControl(ownerDocument: Document, options: {
    open: boolean;
    query: string;
    onOpen: () => void;
    onQuery: (query: string) => void;
    onNext: () => void;
    onPrevious: () => void;
    onActivate: () => void;
    onClose: () => void;
}): SearchControlDom;
//# sourceMappingURL=controls.d.ts.map