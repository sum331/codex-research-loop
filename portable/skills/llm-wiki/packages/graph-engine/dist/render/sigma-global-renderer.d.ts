import type { ThemeId } from "../types";
import type { SigmaGlobalRenderer, SigmaGlobalRendererCreateOptions, SigmaGlobalRendererRuntimeBoundary } from "./sigma-global-types";
export type { SigmaGlobalCameraState, SigmaGlobalGraphologyGraph, SigmaGlobalGraphologyRuntime, SigmaGlobalRenderer, SigmaGlobalRendererCreateOptions, SigmaGlobalRendererRuntime, SigmaGlobalRendererRuntimeBoundary, SigmaGlobalRendererUpdateOptions, SigmaGlobalSigmaLike } from "./sigma-global-types";
export declare const SIGMA_GLOBAL_RENDERER_ID: "sigma-global";
export declare const SIGMA_GLOBAL_RENDERER_ROUTE_MANAGER_OWNER: "facade";
export declare const SIGMA_GLOBAL_RENDERER_BUNDLE_BOUNDARY: {
    readonly sigma: "runtime-loaded-by-sigma-global-renderer";
    readonly graphology: "runtime-loaded-by-sigma-global-renderer";
    readonly workbench: "loads through the graph-engine ESM Sigma runtime boundary when global route manager selects Sigma";
    readonly offlineHtml: "loads through the graph-engine IIFE Sigma runtime boundary when offline global route manager selects Sigma";
};
export declare function sigmaGlobalRendererRuntimeBoundary(): Promise<SigmaGlobalRendererRuntimeBoundary>;
export declare function createSigmaGlobalRenderer(options: SigmaGlobalRendererCreateOptions): SigmaGlobalRenderer;
/** @internal 仅为单元测试直接断言而导出，非稳定公开 API；唯一生产调用方是本文件 createSigmaRoot。 */
export declare function sigmaSettingsForTheme(theme: ThemeId): Record<string, unknown>;
//# sourceMappingURL=sigma-global-renderer.d.ts.map