// CIELAB at D50 ↔ XYZ_D65
//
// Traditional CIELAB (ICC PCS standard) uses D50 reference white. This module
// implements CIELAB_D50 by bridging through Bradford CAT to/from the D65 hub.
//
// For modern display work, use `src/spaces/cielab.ts` (D65 variant).
// For ICC profile work, this D50 variant is the right choice.
//
// Primary source: CIE 015:2018 + ICC.1:2010 (D50 PCS convention).
import { d65ToD50, d50ToD65, D50 } from '../adaptation/bradford.js';
// D50 reference white in 0-1 scale.
const Xn = D50[0];
const Yn = D50[1];
const Zn = D50[2];
const DELTA = 6 / 29;
const DELTA_CUBED = DELTA * DELTA * DELTA;
const THREE_DELTA_SQ = 3 * DELTA * DELTA;
const FOUR_OVER_29 = 4 / 29;
function f(t) {
    if (t > DELTA_CUBED)
        return Math.cbrt(t);
    return t / THREE_DELTA_SQ + FOUR_OVER_29;
}
function fInverse(t) {
    if (t > DELTA)
        return t * t * t;
    return THREE_DELTA_SQ * (t - FOUR_OVER_29);
}
export function fromXYZ(c) {
    const xyz_d50 = d65ToD50(c);
    const fx = f(xyz_d50[0] / Xn);
    const fy = f(xyz_d50[1] / Yn);
    const fz = f(xyz_d50[2] / Zn);
    return [
        116 * fy - 16,
        500 * (fx - fy),
        200 * (fy - fz),
    ];
}
export function toXYZ(c) {
    const fy = (c[0] + 16) / 116;
    const fx = fy + c[1] / 500;
    const fz = fy - c[2] / 200;
    const xyz_d50 = [
        Xn * fInverse(fx),
        Yn * fInverse(fy),
        Zn * fInverse(fz),
    ];
    return d50ToD65(xyz_d50);
}
export const testVectors = [
    {
        input: { 0: 0, 1: 0, 2: 0, length: 3 },
        output: [0, 0, 0],
        tolerance: 1e-3,
        source: 'Black point — L*=0, a*=b*=0',
    },
    {
        input: { 0: 0.9504559270516716, 1: 1.0, 2: 1.0890577507598784, length: 3 },
        output: [100, 0, 0],
        tolerance: 1e-3,
        source: 'D65 white through Bradford → D50 CIELAB (100, 0, 0)',
    },
];
