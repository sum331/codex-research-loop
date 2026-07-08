export type GraphArchitectureLayerId = "data" | "layout" | "viewport" | "controller" | "renderer" | "gestures" | "facade";
export interface GraphArchitectureLayer {
    id: GraphArchitectureLayerId;
    name: string;
    owns: readonly string[];
    entrypoints: readonly string[];
    mustNotOwn: readonly string[];
}
export declare const GRAPH_ARCHITECTURE_LAYERS: readonly [{
    readonly id: "data";
    readonly name: "GraphData";
    readonly owns: readonly ["graph schema", "node and edge facts", "selection data inputs"];
    readonly entrypoints: readonly ["src/types.ts", "src/model/", "src/graph-node.ts", "src/select/"];
    readonly mustNotOwn: readonly ["DOM", "screen projection", "host callbacks", "pointer or wheel events"];
}, {
    readonly id: "layout";
    readonly name: "GraphLayout";
    readonly owns: readonly ["world positions", "layout bounds", "community wash geometry", "spatial hit testing"];
    readonly entrypoints: readonly ["src/layout/", "src/render/model.ts", "src/render/community-wash.ts", "src/sim/"];
    readonly mustNotOwn: readonly ["host callbacks", "browser default policy", "screen projection"];
}, {
    readonly id: "viewport";
    readonly name: "GraphViewport";
    readonly owns: readonly ["camera", "world/screen projection", "fit, pan, zoom, minimap projection", "resize anchoring"];
    readonly entrypoints: readonly ["src/render/viewport.ts", "src/render/geometry.ts"];
    readonly mustNotOwn: readonly ["graph data mutation", "DOM event classification", "host callbacks"];
}, {
    readonly id: "controller";
    readonly name: "GraphController";
    readonly owns: readonly ["semantic graph commands", "keyboard routing", "node drag coordination"];
    readonly entrypoints: readonly ["src/render/controller.ts"];
    readonly mustNotOwn: readonly ["host callbacks", "graph drawing", "render-model computation"];
}, {
    readonly id: "renderer";
    readonly name: "GraphRenderer";
    readonly owns: readonly ["DOM/SVG drawing", "node, edge, wash, toolbar, overlay, reader painting", "render-only CSS state"];
    readonly entrypoints: readonly ["src/render/graph-renderer-root.ts", "src/render/render-pipeline.ts", "src/render/overlays-presenter.ts", "src/render/nodes.ts", "src/render/edges.ts", "src/render/community-washes.ts", "src/render/minimap.ts", "src/render/controls.ts", "src/render/hover-card.ts", "src/render/offline-reader.ts"];
    readonly mustNotOwn: readonly ["host callbacks", "selection semantics", "browser default policy"];
}, {
    readonly id: "gestures";
    readonly name: "GraphGestures";
    readonly owns: readonly ["raw wheel, pointer, and keyboard ownership", "gesture blockers", "graph-owned intent classification"];
    readonly entrypoints: readonly ["src/render/gestures.ts"];
    readonly mustNotOwn: readonly ["host callbacks", "graph drawing", "data persistence"];
}, {
    readonly id: "facade";
    readonly name: "GraphFacade";
    readonly owns: readonly ["public graph engine API", "host capability callbacks", "selection resolution", "renderer lifecycle"];
    readonly entrypoints: readonly ["src/facade.ts", "src/index.ts"];
    readonly mustNotOwn: readonly ["raw DOM event policy", "node layout physics", "drawing internals"];
}];
//# sourceMappingURL=architecture.d.ts.map