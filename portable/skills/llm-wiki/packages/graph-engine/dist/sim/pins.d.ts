import type { NodeId, PinMap, PinPosition } from "../types";
import type { RenderPositionMap, RenderableGraph } from "../render";
export interface PinStateSnapshot {
    pins: PinMap;
    pinnedNodeIds: NodeId[];
}
export declare class PinState {
    private readonly nodePathById;
    private readonly nodeIdByPath;
    private pins;
    constructor(graph: RenderableGraph, pins?: PinMap);
    isPinned(id: NodeId): boolean;
    pin(id: NodeId, position: PinPosition): PinStateSnapshot;
    unpin(id: NodeId): PinStateSnapshot;
    reset(): PinStateSnapshot;
    snapshot(): PinStateSnapshot;
}
export declare function pinsToPositions(graph: RenderableGraph, pins: PinMap): RenderPositionMap;
//# sourceMappingURL=pins.d.ts.map