import type { ThemeId } from "../types";
export interface ThemeTokens {
    id: ThemeId;
    colorScheme: "light" | "dark";
    vars: Record<string, string>;
    communityColors: string[];
}
export declare function parseCssTokens(cssText: string): Record<string, string>;
export declare const THEMES: Record<ThemeId, ThemeTokens>;
export declare function getThemeTokens(theme: ThemeId): ThemeTokens;
export declare function themeTokensToCssVars(theme: ThemeId | ThemeTokens): Record<string, string>;
export declare function getCommunityColor(theme: ThemeId | ThemeTokens, index: number): string;
//# sourceMappingURL=tokens.d.ts.map