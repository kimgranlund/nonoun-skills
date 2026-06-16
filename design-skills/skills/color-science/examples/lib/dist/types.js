// Color math system — branded types and shared primitives.
//
// Every color in this system is a [number, number, number] tuple at runtime,
// but the compiler distinguishes between color spaces via branded types.
// This catches space-mixing errors at compile time with zero runtime cost.
//
// See references/ARCHITECTURE.md for the full design rationale.
// ─── Construction helpers (brand a tuple without runtime cost) ────────────────
export const xyz = (X, Y, Z) => [X, Y, Z];
export const linearSRGB = (R, G, B) => [R, G, B];
export const encodedSRGB = (R, G, B) => [R, G, B];
export const linearP3 = (R, G, B) => [R, G, B];
export const linearRec2020 = (R, G, B) => [R, G, B];
export const oklab = (L, a, b) => [L, a, b];
export const oklch = (L, C, h) => [L, C, h];
export const cielab_D65 = (L, a, b) => [L, a, b];
export const cielch_D65 = (L, C, h) => [L, C, h];
export const xyY = (x, y, Y) => [x, y, Y];
export const okhsl = (h, s, l) => [h, s, l];
export const okhsv = (h, s, v) => [h, s, v];
export const hct = (h, c, t) => [h, c, t];
export const ciecam16_JMh = (J, M, h) => [J, M, h];
/** Multiply a 3x3 matrix by a 3-vector. Returns a plain mutable tuple — caller brands it. */
export function mulMat3Vec3(m, v) {
    return [
        m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
        m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
        m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2],
    ];
}
/** Multiply two 3x3 matrices. Useful for pre-composing transforms (e.g., M_XYZ→sRGB * M_adapt). */
export function mulMat3Mat3(a, b) {
    const r = (i, j) => a[i][0] * b[0][j] + a[i][1] * b[1][j] + a[i][2] * b[2][j];
    return [
        [r(0, 0), r(0, 1), r(0, 2)],
        [r(1, 0), r(1, 1), r(1, 2)],
        [r(2, 0), r(2, 1), r(2, 2)],
    ];
}
// ─── Sign-preserving cube root (used by OKLab, CIELAB, others) ────────────────
/** Sign-preserving cube root. Required when LMS or XYZ values can be negative (out of gamut). */
export const cbrt = (x) => Math.sign(x) * Math.pow(Math.abs(x), 1 / 3);
// ─── Hue wrapping (used by polar spaces) ──────────────────────────────────────
/** Normalize a hue angle in degrees to [0, 360). */
export const wrapHueDeg = (h) => {
    const r = h % 360;
    return r < 0 ? r + 360 : r;
};
// ─── Tolerance for round-trip checks ──────────────────────────────────────────
/** Max L∞ distance considered equal for linear (matrix-only) round-trips. */
export const LINEAR_TOLERANCE = 1e-9;
/** Max L∞ distance considered equal for nonlinear (cube root, gamma) round-trips. */
export const NONLINEAR_TOLERANCE = 1e-4;
/** L∞ distance between two tuples. */
export function lInfDistance(a, b) {
    return Math.max(Math.abs(a[0] - b[0]), Math.abs(a[1] - b[1]), Math.abs(a[2] - b[2]));
}
