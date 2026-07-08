import type { GraphDiff } from "../types";
export type DiffQueueVisibility = "visible" | "hidden";
export type DiffQueueDragState = "idle" | "dragging";
export type DiffQueueReason = "visible" | "hidden" | "dragging";
export interface DiffQueueSnapshot {
    pending: GraphDiff | null;
    isAnimating: boolean;
    visibility: DiffQueueVisibility;
    dragState: DiffQueueDragState;
}
export interface DiffQueueDecision {
    action: "consume" | "queue";
    diff: GraphDiff | null;
    reason: DiffQueueReason;
    snapshot: DiffQueueSnapshot;
}
export declare class GraphDiffQueue {
    private pending;
    private visibility;
    private dragState;
    private isAnimating;
    constructor(options?: {
        visible?: boolean;
    });
    get snapshot(): DiffQueueSnapshot;
    push(diff: GraphDiff | null): DiffQueueDecision;
    setVisible(visible: boolean): DiffQueueDecision;
    setDragging(dragging: boolean): DiffQueueDecision;
    finishAnimation(): DiffQueueDecision;
    clear(): void;
    private flushIfReady;
    private canConsume;
    private blockedReason;
    private decision;
}
export declare function mergeGraphDiffs(previous: GraphDiff | null, next: GraphDiff): GraphDiff;
export declare function isEmptyDiff(diff: GraphDiff): boolean;
//# sourceMappingURL=index.d.ts.map