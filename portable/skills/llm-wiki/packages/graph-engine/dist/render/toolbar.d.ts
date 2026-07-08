export type GraphToolbarPanelState = "closed" | "filters" | "legend";
export interface GraphToolbarStorage {
    getItem(key: string): string | null;
    setItem(key: string, value: string): void;
}
export declare const GRAPH_TOOLBAR_PANEL_KEY = "llm-wiki:graph:toolbar:panel";
export declare function normalizeToolbarPanelState(value: unknown): GraphToolbarPanelState;
export declare function readToolbarPanelState(storage: GraphToolbarStorage | null | undefined): GraphToolbarPanelState;
export declare function writeToolbarPanelState(storage: GraphToolbarStorage | null | undefined, state: GraphToolbarPanelState): void;
export declare function nextToolbarPanelState(current: GraphToolbarPanelState, requested: Exclude<GraphToolbarPanelState, "closed">): GraphToolbarPanelState;
export declare function shouldBlankClickCloseToolbar(state: GraphToolbarPanelState): boolean;
export declare function toolbarPanelStateAfterBlankClick(state: GraphToolbarPanelState): GraphToolbarPanelState;
//# sourceMappingURL=toolbar.d.ts.map