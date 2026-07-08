import { type SimulationNodeDatum } from "d3-force";
import type { NodeId } from "../types";
import type { RenderPositionMap, RenderableGraph } from "../render";
export { PinState, pinsToPositions } from "./pins";
export type { PinStateSnapshot } from "./pins";
export interface LiveSimulationNode extends SimulationNodeDatum {
    id: NodeId;
    baseX: number;
    baseY: number;
    sourcePath: string;
    fixedByDrag?: boolean;
    savedFx?: number | null;
    savedFy?: number | null;
}
export interface LiveGraphSimulationOptions {
    coldStartAlpha?: number;
    lowHeatAlphaTarget?: number;
    alphaMin?: number;
    alphaDecay?: number;
    velocityDecay?: number;
    dragBounds?: GraphLayoutBounds;
    onTick?: (snapshot: LiveGraphSimulationSnapshot) => void;
}
export interface LiveGraphSimulationSnapshot {
    alpha: number;
    positions: RenderPositionMap;
}
export interface DragEndOptions {
    keepFixed?: boolean;
    restore?: {
        position: {
            x: number;
            y: number;
        };
        fixed: boolean;
    };
}
export interface GraphLayoutBounds {
    minX: number;
    minY: number;
    maxX: number;
    maxY: number;
}
export declare const DEFAULT_GRAPH_LAYOUT_BOUNDS: GraphLayoutBounds;
export declare class LiveGraphSimulation {
    private readonly options;
    readonly nodes: LiveSimulationNode[];
    private readonly simulation;
    private readonly nodeById;
    private readonly directNeighbors;
    private readonly dragBounds;
    private readonly onTick?;
    private draggedNodeId;
    private destroyed;
    constructor(graph: RenderableGraph, options?: LiveGraphSimulationOptions);
    get alpha(): number;
    get coldStartAlpha(): number;
    get lowHeatAlphaTarget(): number;
    get alphaMin(): number;
    get alphaDecay(): number;
    get velocityDecay(): number;
    startCold(): void;
    tick(count?: number): LiveGraphSimulationSnapshot;
    settle(maxTicks?: number): LiveGraphSimulationSnapshot;
    beginDrag(id: NodeId): LiveSimulationNode;
    dragTo(id: NodeId, position: {
        x: number;
        y: number;
    }): LiveSimulationNode;
    setFixed(id: NodeId, position: {
        x: number;
        y: number;
    } | null): LiveSimulationNode;
    endDrag(options?: DragEndOptions): LiveGraphSimulationSnapshot;
    snapshot(): LiveGraphSimulationSnapshot;
    destroy(): void;
    private requireNode;
    private freezeFarNodes;
    private unfreezeFarNodes;
    private emitTick;
    private assertActive;
}
export declare function createLiveGraphSimulation(graph: RenderableGraph, options?: LiveGraphSimulationOptions): LiveGraphSimulation;
export declare function constrainDragTargetToLayoutBounds(position: {
    x: number;
    y: number;
}, options?: {
    bounds?: GraphLayoutBounds;
    fallback?: {
        x: number;
        y: number;
    };
}): {
    x: number;
    y: number;
};
//# sourceMappingURL=index.d.ts.map