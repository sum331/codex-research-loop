export interface CommunityWashPoint {
    x: number;
    y: number;
}
export interface CommunityWashNodeLike {
    point: CommunityWashPoint;
}
export interface CommunityWash {
    cx: number;
    cy: number;
    rx: number;
    ry: number;
    opacity: number;
}
export interface CommunityWashOptions {
    minRadiusX?: number;
    minRadiusY?: number;
    paddingX?: number;
    paddingY?: number;
    maxRadiusX?: number;
    maxRadiusY?: number;
}
export declare const DEFAULT_COMMUNITY_WASH_MAX_RADIUS_X: number;
export declare const DEFAULT_COMMUNITY_WASH_MAX_RADIUS_Y: number;
export declare function computeCommunityWash(nodes: CommunityWashNodeLike[], options?: CommunityWashOptions): CommunityWash | null;
//# sourceMappingURL=community-wash.d.ts.map