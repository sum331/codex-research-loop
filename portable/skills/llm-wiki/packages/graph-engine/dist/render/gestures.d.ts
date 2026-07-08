import type { CommunityId, NodeId } from "../types";
import type { GraphSpatialHitTarget } from "../layout";
export type GraphGestureTargetKind = "graph-blank" | "node" | "community-wash" | "aggregation-container" | "edge" | "minimap" | "toolbar" | "search" | "legend" | "drawer" | "text-control" | "unknown";
export type GraphOwnedTargetKind = "graph-blank" | "node" | "community-wash" | "aggregation-container" | "edge";
export type GraphGestureBlockerTargetKind = Exclude<GraphGestureTargetKind, GraphOwnedTargetKind>;
export type GraphGestureTargetOwnership = "graph-owned" | "graph-blocker";
export interface GraphGestureTargetLike {
    closest?: (selector: string) => GraphGestureTargetLike | null;
    dataset?: Record<string, string | undefined>;
    tagName?: string;
    type?: string;
    isContentEditable?: boolean;
}
export type GraphGestureTarget = {
    kind: "graph-blank";
} | {
    kind: "node";
    id: NodeId | null;
} | {
    kind: "community-wash";
    id: CommunityId | null;
} | {
    kind: "aggregation-container";
    id: string | null;
    communityId: CommunityId | null;
} | {
    kind: "edge";
    id: string | null;
} | {
    kind: "minimap";
} | {
    kind: "toolbar";
} | {
    kind: "search";
} | {
    kind: "legend";
} | {
    kind: "drawer";
} | {
    kind: "text-control";
} | {
    kind: "unknown";
};
export declare const GRAPH_OWNED_TARGET_KINDS: readonly ["graph-blank", "node", "community-wash", "aggregation-container", "edge"];
export declare const GRAPH_GESTURE_BLOCKER_TARGET_KINDS: readonly ["minimap", "toolbar", "search", "legend", "drawer", "text-control", "unknown"];
export declare const GRAPH_GESTURE_SELECTORS: {
    readonly textControl: "textarea, select, [contenteditable=\"true\"], [data-graph-text-control=\"true\"]";
    readonly search: ".graph-search";
    readonly toolbar: ".graph-toolbar";
    readonly legend: ".community-legend";
    readonly drawer: ".graph-reader, .graph-selection-panel, [data-graph-drawer=\"true\"]";
    readonly minimap: ".mini-map";
    readonly node: ".node";
    readonly aggregationContainer: ".aggregation-container";
    readonly communityWash: ".community-wash";
    readonly edge: ".edge";
    readonly blank: "[data-graph-blank=\"true\"]";
};
export type GraphWheelTargetDecision = {
    intent: "zoom";
    target: GraphGestureTarget;
} | {
    intent: "blocked";
    target: GraphGestureTarget;
};
export type GraphPointerDownTargetDecision = {
    intent: "node-drag-candidate";
    target: Extract<GraphGestureTarget, {
        kind: "node";
    }>;
} | {
    intent: "community-click-candidate";
    target: Extract<GraphGestureTarget, {
        kind: "community-wash";
    }>;
} | {
    intent: "blank-pan-candidate";
    target: Extract<GraphGestureTarget, {
        kind: "graph-blank" | "edge";
    }>;
} | {
    intent: "blocked";
    target: Exclude<GraphGestureTarget, {
        kind: "node" | "community-wash" | "graph-blank" | "edge";
    }>;
};
export interface GraphWheelEventLike {
    ctrlKey?: boolean;
    metaKey?: boolean;
}
export interface GraphPointerEventLike {
    pointerId: number;
    screenPoint: {
        x: number;
        y: number;
    };
    shiftKey?: boolean;
}
export interface GraphGestureStateMachineOptions {
    dragThreshold?: number;
}
export interface GraphGestureControllerOptions {
    stateMachine?: GraphGestureStateMachine;
    targetFromEventTarget?: (target: EventTarget | null) => GraphGestureTargetLike | null;
    graphTargetFromScreenPoint?: (screenPoint: {
        x: number;
        y: number;
    }) => GraphGestureTarget;
    onWheelZoom: (event: WheelEvent, decision: Extract<GraphWheelTargetDecision, {
        intent: "zoom";
    }>, screenPoint: {
        x: number;
        y: number;
    }) => void;
    onPointerDown?: (event: PointerEvent, decision: Exclude<GraphPointerDownTargetDecision, {
        intent: "blocked";
    }>) => void;
    onGestureIntents: (intents: GraphGestureIntent[], event: PointerEvent | null) => void;
    onActiveStateChange?: (active: GraphGestureActiveState) => void;
    onBlankDoubleClick?: (event: MouseEvent) => void;
}
export type GraphGestureActiveState = {
    kind: "node";
    pointerId: number;
    nodeId: NodeId | null;
    startScreenPoint: {
        x: number;
        y: number;
    };
    lastScreenPoint: {
        x: number;
        y: number;
    };
    additive: boolean;
    locked: boolean;
} | {
    kind: "community-wash";
    pointerId: number;
    communityId: CommunityId | null;
    startScreenPoint: {
        x: number;
        y: number;
    };
    lastScreenPoint: {
        x: number;
        y: number;
    };
    locked: boolean;
    cancelled: boolean;
} | {
    kind: "blank-pan";
    pointerId: number;
    startScreenPoint: {
        x: number;
        y: number;
    };
    lastScreenPoint: {
        x: number;
        y: number;
    };
    locked: boolean;
} | null;
export type GraphGestureIntent = {
    kind: "node-click";
    nodeId: NodeId | null;
    additive: boolean;
    pointerId: number;
} | {
    kind: "node-drag-start";
    nodeId: NodeId | null;
    pointerId: number;
    screenPoint: {
        x: number;
        y: number;
    };
} | {
    kind: "node-drag-move";
    nodeId: NodeId | null;
    pointerId: number;
    screenPoint: {
        x: number;
        y: number;
    };
    delta: {
        x: number;
        y: number;
    };
} | {
    kind: "node-drag-end";
    nodeId: NodeId | null;
    pointerId: number;
    screenPoint: {
        x: number;
        y: number;
    };
} | {
    kind: "node-drag-cancel";
    nodeId: NodeId | null;
    pointerId: number;
    reason: "pointercancel" | "lostpointercapture" | "escape";
} | {
    kind: "community-click";
    communityId: CommunityId | null;
    pointerId: number;
} | {
    kind: "community-click-cancelled";
    communityId: CommunityId | null;
    pointerId: number;
    reason: "moved" | "pointercancel" | "lostpointercapture" | "escape";
} | {
    kind: "blank-click";
    pointerId: number;
} | {
    kind: "blank-pan-start";
    pointerId: number;
    screenPoint: {
        x: number;
        y: number;
    };
} | {
    kind: "blank-pan-move";
    pointerId: number;
    screenPoint: {
        x: number;
        y: number;
    };
    delta: {
        x: number;
        y: number;
    };
} | {
    kind: "blank-pan-end";
    pointerId: number;
    screenPoint: {
        x: number;
        y: number;
    };
} | {
    kind: "blank-pan-cancel";
    pointerId: number;
    reason: "pointercancel" | "lostpointercapture" | "escape";
};
export declare function classifyGraphEventTarget(target: GraphGestureTargetLike | null | undefined): GraphGestureTarget;
export declare function graphGestureTargetOwnership(target: GraphGestureTarget): GraphGestureTargetOwnership;
export declare function isGraphOwnedGestureTarget(target: GraphGestureTarget): target is Extract<GraphGestureTarget, {
    kind: GraphOwnedTargetKind;
}>;
export declare function isGraphGestureBlockerTarget(target: GraphGestureTarget): target is Extract<GraphGestureTarget, {
    kind: GraphGestureBlockerTargetKind;
}>;
export declare function classifyGraphWheelTarget(target: GraphGestureTargetLike | null | undefined, event?: GraphWheelEventLike): GraphWheelTargetDecision;
export declare function classifyGraphWheelTargetFromGraphTarget(graphTarget: GraphGestureTarget, event?: GraphWheelEventLike): GraphWheelTargetDecision;
export declare function classifyGraphPointerDownTarget(target: GraphGestureTargetLike | null | undefined): GraphPointerDownTargetDecision;
export declare function graphSpatialHitToGestureTarget(hit: GraphSpatialHitTarget | null | undefined): GraphGestureTarget;
export declare function classifyGraphPointerDownTargetFromGraphTarget(graphTarget: GraphGestureTarget): GraphPointerDownTargetDecision;
export declare class GraphGestureStateMachine {
    private readonly dragThreshold;
    private active;
    constructor(options?: GraphGestureStateMachineOptions);
    snapshot(): GraphGestureActiveState;
    pointerDown(decision: GraphPointerDownTargetDecision, event: GraphPointerEventLike): GraphGestureIntent[];
    pointerMove(event: GraphPointerEventLike): GraphGestureIntent[];
    pointerUp(event: GraphPointerEventLike): GraphGestureIntent[];
    pointerCancel(event: Pick<GraphPointerEventLike, "pointerId">): GraphGestureIntent[];
    lostPointerCapture(event: Pick<GraphPointerEventLike, "pointerId">): GraphGestureIntent[];
    escape(): GraphGestureIntent[];
    private cancel;
}
export declare class GraphGestureController {
    private readonly root;
    private readonly options;
    private readonly stateMachine;
    private lastBlankDoubleClick;
    private readonly recentPointerDownTargets;
    private destroyed;
    constructor(root: HTMLElement, options: GraphGestureControllerOptions);
    destroy(): void;
    snapshot(): GraphGestureActiveState;
    escape(): GraphGestureIntent[];
    private readonly handleWheel;
    private readonly handlePointerDown;
    private readonly handlePointerMove;
    private readonly handlePointerUp;
    private readonly handlePointerCancel;
    private readonly handleLostPointerCapture;
    private readonly handleClick;
    private readonly handleDoubleClick;
    private triggerBlankDoubleClick;
    private isDuplicateBlankDoubleClick;
    private isTrueBlankDoubleClick;
    private recordPointerDown;
    private applyIntents;
    private emitActiveState;
    private eventTarget;
    private graphTargetForEvent;
    private pointerEventFromPointerEvent;
    private screenPointFromMouseEvent;
}
//# sourceMappingURL=gestures.d.ts.map