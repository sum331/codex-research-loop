export interface SigmaGlobalPointerEventPayload {
    node?: unknown;
    event?: {
        x?: unknown;
        y?: unknown;
        preventSigmaDefault?: () => void;
    };
    x?: unknown;
    y?: unknown;
    preventSigmaDefault?: () => void;
}
export declare function preventSigmaDefault(payload: unknown): void;
//# sourceMappingURL=sigma-events.d.ts.map