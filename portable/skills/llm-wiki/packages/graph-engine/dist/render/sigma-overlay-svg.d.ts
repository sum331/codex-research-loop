import type { SigmaCommunityCloud } from "./community-cloud-geometry";
export declare const SIGMA_OVERLAY_SVG_NS = "http://www.w3.org/2000/svg";
export declare function createSigmaOverlayRoot(root: HTMLElement): HTMLElement;
export declare function sigmaOverlayButton(ownerDocument: Document, kind: string, id: string, label: string): HTMLButtonElement;
export declare function sigmaOverlayPassiveElement(ownerDocument: Document, kind: string, id: string): HTMLDivElement;
export declare function applyOverlayBox(element: HTMLElement, box: {
    left: number;
    top: number;
    width: number;
    height: number;
}): void;
export declare function nextSigmaCloudFilterSequence(): number;
export declare function sigmaSharedCloudFilterDef(ownerDocument: Document, filterId: string): SVGSVGElement;
export type SigmaCloudKind = "polygon" | "ellipse";
export interface SigmaCloudSvgHandle {
    svg: SVGSVGElement;
    shape: SVGElement;
    kind: SigmaCloudKind;
}
export declare function createSigmaCloudSvg(ownerDocument: Document, cloud: SigmaCommunityCloud, filterId: string, onSelect: () => void): SigmaCloudSvgHandle;
export declare function applySigmaCloudColor(shape: SVGElement, color: string, dim: boolean): void;
export declare function applySigmaCloudGeometry(shape: SVGElement, kind: SigmaCloudKind, cloud: SigmaCommunityCloud): void;
//# sourceMappingURL=sigma-overlay-svg.d.ts.map