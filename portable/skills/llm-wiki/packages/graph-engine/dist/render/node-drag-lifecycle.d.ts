import type { LiveGraphSimulation, PinState } from "../sim";
import type { NodeId, PinMap, PinPosition } from "../types";
import type { RenderPositionMap } from "./model";
export interface GraphNodeDragSession {
    pointerId: number;
    nodeId: NodeId;
    startWorldPoint: PinPosition;
    wasPinned: boolean;
}
export interface CommitGraphNodeDragInput {
    nodeId: NodeId;
    simulation: LiveGraphSimulation;
    pinState: PinState;
    finalWorldPoint?: PinPosition | null;
}
export interface CancelGraphNodeDragInput {
    session: GraphNodeDragSession;
    simulation: LiveGraphSimulation;
    pinState: PinState;
}
export interface CommittedGraphNodeDrag {
    kind: "committed";
    nodeId: NodeId;
    pinPosition: PinPosition;
    positions: RenderPositionMap;
    pins: PinMap;
    pinnedNodeIds: NodeId[];
}
export interface CancelledGraphNodeDrag {
    kind: "cancelled";
    nodeId: NodeId;
    restoredPosition: PinPosition;
    restoredFixed: boolean;
    positions: RenderPositionMap;
    pins: PinMap;
    pinnedNodeIds: NodeId[];
}
export declare function commitGraphNodeDrag(input: CommitGraphNodeDragInput): CommittedGraphNodeDrag;
export declare function cancelGraphNodeDrag(input: CancelGraphNodeDragInput): CancelledGraphNodeDrag;
export interface FrozenGraphNodeDragInput {
    nodeId: NodeId;
    startWorldPoint: PinPosition;
    wasPinned: boolean;
    finalWorldPoint?: PinPosition | null;
    currentPositions: RenderPositionMap;
    pinState: PinState;
}
export declare function commitFrozenGraphNodeDrag(input: FrozenGraphNodeDragInput): CommittedGraphNodeDrag;
export declare function cancelFrozenGraphNodeDrag(input: FrozenGraphNodeDragInput): CancelledGraphNodeDrag;
//# sourceMappingURL=node-drag-lifecycle.d.ts.map