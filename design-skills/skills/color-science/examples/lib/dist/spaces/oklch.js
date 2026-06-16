// OKLCH ↔ XYZ_D65 (via OKLab)
//
// OKLCH = polar form of OKLab. The CSS convention for hue is degrees.
//
// [L, C, h_degrees] where:
//   L = OKLab L (lightness)
//   C = sqrt(a² + b²)       (chroma)
//   h = atan2(b, a) in degrees, normalized to [0, 360)
//
// Hub conversion goes through OKLab → XYZ_D65.
import { oklch, oklab, xyz, wrapHueDeg } from '../types.js';
import * as oklabSpace from './oklab.js';
const DEG_TO_RAD = Math.PI / 180;
const RAD_TO_DEG = 180 / Math.PI;
/** OKLab → OKLCH (polar form). */
export function fromOKLab(lab) {
    const [L, a, b] = lab;
    const C = Math.sqrt(a * a + b * b);
    let h = Math.atan2(b, a) * RAD_TO_DEG;
    if (h < 0)
        h += 360;
    return oklch(L, C, h);
}
/** OKLCH → OKLab (cartesian form). */
export function toOKLab(lch) {
    const [L, C, hDeg] = lch;
    const h = wrapHueDeg(hDeg) * DEG_TO_RAD;
    return oklab(L, C * Math.cos(h), C * Math.sin(h));
}
export function fromXYZ(c) {
    return fromOKLab(oklabSpace.fromXYZ(c));
}
export function toXYZ(c) {
    return oklabSpace.toXYZ(toOKLab(c));
}
export const testVectors = [
    // Note: achromatic points (C=0) have indeterminate hue. Float noise produces
    // arbitrary hue values that fail strict round-trip. Test vectors below use
    // chromatic inputs where (L, C, h) are all well-defined.
    {
        input: xyz(0.4123907993, 0.2126390059, 0.0193308187), // pure sRGB red
        output: oklch(0.6279554, 0.2576, 29.2339),
        tolerance: 1e-2,
        source: 'OKLab pure sRGB red — chromatic, hue well-defined',
    },
];
