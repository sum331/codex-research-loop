import type { CommunityId, NodeId, PinMap, SelectionInput } from "../types";
import type { RenderPositionMap } from "./model";
import { type RendererViewport } from "./viewport";
export type GraphRuntimeHoverTarget = {
    kind: "node";
    id: NodeId;
} | {
    kind: "edge";
    id: string;
} | {
    kind: "community";
    id: CommunityId;
} | null;
export type GraphRuntimeFocusTarget = {
    kind: "community";
    id: CommunityId;
} | null;
export type GraphRuntimeSelectionSurface = "reader" | "selection-panel" | null;
export type GraphRuntimeGestureState = {
    kind: "node-drag";
    pointerId: number;
    nodeId: NodeId;
    grabOffset: {
        x: number;
        y: number;
    };
    startWorldPoint: {
        x: number;
        y: number;
    };
    wasPinned: boolean;
    locked: boolean;
} | {
    kind: "viewport-pan";
    pointerId: number;
    lastScreenPoint: {
        x: number;
        y: number;
    };
    locked: boolean;
} | {
    kind: "community-click";
    pointerId: number;
    communityId: CommunityId;
    locked: boolean;
} | null;
export interface GraphRuntimeStateSnapshot {
    viewport: RendererViewport;
    positions: RenderPositionMap;
    pins: PinMap;
    hover: GraphRuntimeHoverTarget;
    selection: SelectionInput | null;
    selectionSurface: GraphRuntimeSelectionSurface;
    focus: GraphRuntimeFocusTarget;
    activeGesture: GraphRuntimeGestureState;
}
export interface GraphRuntimeStateOptions {
    viewport?: Partial<RendererViewport> | null;
    positions?: RenderPositionMap;
    pins?: PinMap;
    hover?: GraphRuntimeHoverTarget;
    selection?: SelectionInput | null;
    selectionSurface?: GraphRuntimeSelectionSurface;
    focus?: GraphRuntimeFocusTarget;
    activeGesture?: GraphRuntimeGestureState;
}
export type GraphRuntimeStateListener = (snapshot: GraphRuntimeStateSnapshot) => void;
export declare class GraphRuntimeState {
    private snapshotValue;
    private readonly listeners;
    constructor(options?: GraphRuntimeStateOptions);
    snapshot(): GraphRuntimeStateSnapshot;
    subscribe(listener: GraphRuntimeStateListener): () => void;
    setViewport(viewport: Partial<RendererViewport> | null | undefined): GraphRuntimeStateSnapshot;
    setPositions(positions: RenderPositionMap): GraphRuntimeStateSnapshot;
    commitPosition(nodeId: NodeId, position: {
        x: number;
        y: number;
    }): GraphRuntimeStateSnapshot;
    setPins(pins: PinMap): GraphRuntimeStateSnapshot;
    setHover(hover: GraphRuntimeHoverTarget): GraphRuntimeStateSnapshot;
    setSelection(selection: SelectionInput | null, selectionSurface?: GraphRuntimeSelectionSurface): GraphRuntimeStateSnapshot;
    setFocus(focus: GraphRuntimeFocusTarget): GraphRuntimeStateSnapshot;
    setActiveGesture(activeGesture: GraphRuntimeGestureState): GraphRuntimeStateSnapshot;
    clearInteraction(): GraphRuntimeStateSnapshot;
    private update;
}
export declare function createGraphRuntimeState(options?: GraphRuntimeStateOptions): GraphRuntimeState;
//# sourceMappingURL=state.d.ts.map