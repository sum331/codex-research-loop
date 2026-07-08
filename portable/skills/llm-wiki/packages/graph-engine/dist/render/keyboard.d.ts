export type GraphKeyboardIntent = "open-search" | "close-search" | "close-toolbar" | "cancel-active-gesture" | "clear-interaction" | "blocked";
export interface GraphKeyboardIntentInput {
    key: string;
    ctrlKey?: boolean;
    metaKey?: boolean;
    graphFocused: boolean;
    activeGesture: boolean;
    textEditingTarget: boolean;
    searchActive: boolean;
    toolbarOpen: boolean;
    interactionActive: boolean;
}
export declare function classifyGraphKeyboardIntent(input: GraphKeyboardIntentInput): GraphKeyboardIntent;
export declare function isTextEditingElement(element: Element | null): boolean;
//# sourceMappingURL=keyboard.d.ts.map