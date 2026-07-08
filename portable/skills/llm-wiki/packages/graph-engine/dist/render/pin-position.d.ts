import { type PinPosition } from "../types";
export interface WorldPinPoint {
    x: number;
    y: number;
}
export declare function normalizeStoredPinPosition(position: PinPosition): PinPosition;
export declare function normalizeWorldPinPosition(position: PinPosition): PinPosition;
export declare function pinPositionToWorldPoint(position: PinPosition): WorldPinPoint;
//# sourceMappingURL=pin-position.d.ts.map