declare function splitLabelGraphemes(label: any): unknown[];
declare function labelCharWidth(grapheme: any): number;
declare function measureLabelWidth(graphemes: any): number;
declare function truncateLabel(label: any, maxWidth: any): {
    text: string;
    truncated: boolean;
};
declare function cardDims(n: any): {
    w: number;
    h: number;
};
declare function createSafeStorage(storage: any, logger: any): {
    get: (key: any) => any;
    set: (key: any, value: any) => void;
};
declare function getWikiStorageNamespace(meta: any, pathname: any): string;
declare function defaultQueue(): {
    version: number;
    favorites: never[];
    notes: never[];
    recentNoteIds: never[];
};
declare function normalizeQueue(raw: any): {
    version: number;
    favorites: any;
    notes: any;
    recentNoteIds: any;
};
declare function toggleQueueFavorite(queue: any, nodeId: any): {
    version: number;
    favorites: any;
    notes: any;
    recentNoteIds: any;
};
declare function appendQueueNote(queue: any, note: any, limit: any): {
    version: number;
    favorites: any;
    notes: any;
    recentNoteIds: any;
};
declare function summarizeQueue(queue: any, nodesById: any, limit: any): {
    favorite_count: any;
    note_count: any;
    recent_items: {
        kind: string;
        node_id: any;
        label: any;
        text: any;
    }[];
};
declare function defaultLearning(): {
    version: number;
    entry: {
        recommended_start_node_id: null;
        recommended_start_reason: null;
        default_mode: string;
    };
    views: {
        path: {
            enabled: boolean;
            start_node_id: null;
            node_ids: never[];
            degraded: boolean;
        };
        community: {
            enabled: boolean;
            community_id: null;
            label: null;
            node_ids: never[];
            is_weak: boolean;
            degraded: boolean;
        };
        global: {
            enabled: boolean;
            node_ids: never[];
            degraded: boolean;
        };
    };
    communities: never[];
    degraded: {
        path_to_community: boolean;
        community_to_global: boolean;
    };
};
declare function normalizeLearning(raw: any): {
    version: any;
    entry: {
        recommended_start_node_id: any;
        recommended_start_reason: any;
        default_mode: any;
    };
    views: {
        path: {
            enabled: any;
            start_node_id: any;
            node_ids: any;
            degraded: any;
        };
        community: {
            enabled: any;
            community_id: any;
            label: any;
            node_ids: any;
            is_weak: any;
            degraded: any;
        };
        global: {
            enabled: any;
            node_ids: any;
            degraded: any;
        };
    };
    communities: any;
    degraded: {
        path_to_community: any;
        community_to_global: any;
    };
};
declare function resolveInitialMode(learning: any): string;
declare function getCommunityNodeIds(nodes: any, communityId: any): any[];
declare function getVisibleNodeIds(learning: any, mode: any): any;
declare function getVisibleLinks(allLinks: any, visibleIds: any): any;
declare function buildSearchHaystack(node: any): string;
declare function buildSearchIndex(nodes: any): {
    node: any;
    haystack: string;
}[];
declare function filterLinksByTypes(allLinks: any, filters: any): any[];
declare function applySearchToNodeIds(searchIndex: any, query: any): any[];
declare function applyFocusMode(options: any): {
    node_ids: any;
    links: any;
};
declare function resolveVisibleSnapshot(options: any): {
    node_ids: any;
    nodes: any;
    links: any;
    searchIndex: {
        node: any;
        haystack: string;
    }[];
};
declare function shouldAutoOpenDrawer(mode: any): boolean;
declare function atlasConfidenceLabel(confidence: any): any;
declare function atlasTypeLabel(type: any): any;
declare function atlasNodeKind(type: any): any;
declare function normalizeAtlasViewport(viewport: any): {
    x: number;
    y: number;
    scale: number;
};
declare function atlasNodePoint(node: any): {
    x: number;
    y: number;
};
declare function getAtlasModelBounds(nodes: any, padding: any): {
    x: number;
    y: number;
    width: number;
    height: number;
    minX: number;
    minY: number;
    maxX: number;
    maxY: number;
};
declare function clampAtlasViewport(viewport: any, viewportSize: any, options: any): {
    x: number;
    y: number;
    scale: number;
};
declare function fitAtlasViewport(bounds: any, viewportSize: any, options: any): {
    x: number;
    y: number;
    scale: number;
};
declare function centerAtlasViewportOnPoint(point: any, viewportSize: any, scale: any, options: any): {
    x: number;
    y: number;
    scale: number;
};
declare function zoomAtlasViewport(viewport: any, factor: any, screenPoint: any, viewportSize: any, options: any): {
    x: number;
    y: number;
    scale: number;
};
declare function atlasViewportRect(viewport: any, viewportSize: any): {
    x: number;
    y: number;
    width: number;
    height: number;
    minX: number;
    minY: number;
    maxX: number;
    maxY: number;
};
declare function atlasPointToMinimap(point: any): {
    x: number;
    y: number;
};
declare function minimapPointToAtlasPoint(point: any): {
    x: number;
    y: number;
};
declare function atlasViewportToMinimapRect(viewport: any, viewportSize: any): {
    x: number;
    y: number;
    width: number;
    height: number;
};
declare function stripAtlasMarkdown(raw: any): string;
declare function buildAtlasModel(rawGraph: any): {
    meta: {
        wiki_title: string;
        total_nodes: any;
        total_edges: any;
        build_date: string;
    };
    nodes: any;
    edges: any;
    byId: {};
    communities: any[];
    communityById: {};
    starts: any[];
    searchIndex: {
        node: any;
        haystack: string;
    }[];
    insights: {
        surprising_connections: any;
        isolated_nodes: any;
        bridge_nodes: any;
        sparse_communities: any;
        meta: any;
    };
};
declare function deriveAtlasLayout(model: any): {
    nodes: any;
    edges: any;
    nodePositions: any;
};
declare function getAtlasDensityMode(count: any): "card" | "compact-card" | "point-plus-focus" | "overview";
declare function resolveAtlasVisibleSnapshot(model: any, layout: any, uiState: any): {
    node_ids: any;
    nodes: any;
    edges: any;
    links: any;
    searchIndex: {
        node: any;
        haystack: string;
    }[];
    densityMode: string;
    labelNodeIds: {};
    matchedNodeIds: {};
    importantNodeIds: {};
    startNodeIds: {};
    starts: any;
    counts: {
        visible_nodes: any;
        visible_edges: any;
        total_nodes: any;
        total_edges: any;
        total_communities: any;
    };
};
declare function resolveAtlasSelectedNodeId(model: any, visibleSnapshot: any, selectedNodeId: any): string | null;
export { splitLabelGraphemes, labelCharWidth, measureLabelWidth, truncateLabel, cardDims, createSafeStorage, getWikiStorageNamespace, defaultQueue, normalizeQueue, toggleQueueFavorite, appendQueueNote, summarizeQueue, defaultLearning, normalizeLearning, resolveInitialMode, getCommunityNodeIds, getVisibleNodeIds, getVisibleLinks, buildSearchHaystack, buildSearchIndex, filterLinksByTypes, applySearchToNodeIds, applyFocusMode, resolveVisibleSnapshot, shouldAutoOpenDrawer, buildAtlasModel, deriveAtlasLayout, resolveAtlasVisibleSnapshot, resolveAtlasSelectedNodeId, getAtlasDensityMode, normalizeAtlasViewport, atlasNodePoint, getAtlasModelBounds, clampAtlasViewport, fitAtlasViewport, centerAtlasViewportOnPoint, zoomAtlasViewport, atlasViewportRect, atlasPointToMinimap, minimapPointToAtlasPoint, atlasViewportToMinimapRect, atlasConfidenceLabel, atlasTypeLabel, atlasNodeKind, stripAtlasMarkdown };
//# sourceMappingURL=legacy-helpers.d.ts.map