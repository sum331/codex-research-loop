import type { GraphRendererAdapterData } from "./adapter";
import type { GraphScreenPoint } from "./geometry";
import type { SigmaGlobalRendererCreateOptions, SigmaGlobalSigmaLike } from "./sigma-global-types";
export interface SigmaCommunityCloud {
    box: {
        left: number;
        top: number;
        width: number;
        height: number;
    };
    localPoints: Array<{
        x: number;
        y: number;
    }> | null;
}
export interface SigmaCommunityCloudBasis {
    hullPoints: Array<{
        x: number;
        y: number;
    }>;
    signature: string;
}
export declare function sigmaCommunityCloudBasisById(adapterData: GraphRendererAdapterData): Map<string, SigmaCommunityCloudBasis>;
export declare function sigmaCommunityCloudBasisByIdWithReuse(previous: Map<string, SigmaCommunityCloudBasis>, adapterData: GraphRendererAdapterData): Map<string, SigmaCommunityCloudBasis>;
export declare function sigmaCommunityCloudBasisByIdWithNodePoint(previous: Map<string, SigmaCommunityCloudBasis>, adapterData: GraphRendererAdapterData, nodeId: string): Map<string, SigmaCommunityCloudBasis>;
export declare function sigmaCommunityCloudSignature(points: readonly {
    x: number;
    y: number;
}[], wash: {
    cx: number;
    cy: number;
    rx: number;
    ry: number;
} | null | undefined): string;
export declare function sigmaProjectedCloudHullPoints(basis: SigmaCommunityCloudBasis | undefined, sigma: SigmaGlobalSigmaLike, options: Pick<SigmaGlobalRendererCreateOptions, "viewport" | "viewportSize" | "adapterData">): GraphScreenPoint[];
export declare function clampPointToWorldEllipse(point: {
    x: number;
    y: number;
}, ellipse: {
    cx: number;
    cy: number;
    rx: number;
    ry: number;
}): {
    x: number;
    y: number;
};
export declare function sigmaCommunityCloud(screenHullPoints: GraphScreenPoint[], fallbackBox: {
    left: number;
    top: number;
    width: number;
    height: number;
}): SigmaCommunityCloud;
export declare function clampPointToScreenEllipse(point: GraphScreenPoint, box: {
    left: number;
    top: number;
    width: number;
    height: number;
}): GraphScreenPoint;
export declare function convexHull2d(points: GraphScreenPoint[]): GraphScreenPoint[];
//# sourceMappingURL=community-cloud-geometry.d.ts.map