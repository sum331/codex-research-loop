import { type GraphWorldBounds } from "./geometry";
export interface RendererViewport {
    x: number;
    y: number;
    scale: number;
}
export interface RendererViewportSize {
    width: number;
    height: number;
}
export interface RendererPoint {
    x: number;
    y: number;
}
export interface WheelDeltaLike {
    deltaY: number;
    deltaMode?: number;
}
export interface RendererViewportOptions {
    minScale?: number;
    maxScale?: number;
    worldBounds?: GraphWorldBounds;
}
export interface RafScheduler {
    requestAnimationFrame(callback: () => void): number;
}
export interface ViewportFrameCommitOptions {
    lightweight?: boolean;
}
export declare const DEFAULT_RENDERER_VIEWPORT: RendererViewport;
export interface RendererViewportResizeOptions extends RendererViewportOptions {
    anchorPoint?: RendererPoint | null;
}
export declare function normalizeRendererViewport(viewport: Partial<RendererViewport> | null | undefined): RendererViewport;
export declare function rendererViewportToTransform(viewport: Partial<RendererViewport> | null | undefined): string;
export declare function applyRendererViewportTransform(layer: HTMLElement, viewport: Partial<RendererViewport> | null | undefined): void;
export declare function normalizeWheelDelta(delta: WheelDeltaLike): number;
export declare function viewportAfterWheelZoom(viewport: Partial<RendererViewport> | null | undefined, delta: WheelDeltaLike, screenPoint: RendererPoint, viewportSize: RendererViewportSize, options?: RendererViewportOptions): RendererViewport;
export declare function panRendererViewport(viewport: Partial<RendererViewport> | null | undefined, delta: RendererPoint, viewportSize: RendererViewportSize, options?: RendererViewportOptions): RendererViewport;
export declare function fitRendererViewportToPoints(points: RendererPoint[], viewportSize: RendererViewportSize, options?: RendererViewportOptions): RendererViewport;
export declare function centerRendererViewportOnPoint(point: RendererPoint, viewport: Partial<RendererViewport> | null | undefined, viewportSize: RendererViewportSize, options?: RendererViewportOptions): RendererViewport;
export declare function viewportAfterResize(viewport: Partial<RendererViewport> | null | undefined, previousSize: RendererViewportSize, nextSize: RendererViewportSize, options?: RendererViewportResizeOptions): RendererViewport;
export declare function rendererViewportToMinimapRect(viewport: Partial<RendererViewport> | null | undefined, viewportSize: RendererViewportSize, options?: RendererViewportOptions): {
    x: number;
    y: number;
    width: number;
    height: number;
};
export declare function createViewportFrameCommitter(commit: (viewport: RendererViewport, options?: ViewportFrameCommitOptions) => void, scheduler?: RafScheduler): {
    schedule(viewport: Partial<RendererViewport>, options?: ViewportFrameCommitOptions): void;
};
//# sourceMappingURL=viewport.d.ts.map