// Adobe RGB (1998) gamma — pure 2.2 power.
//
// Unlike sRGB's piecewise transfer, Adobe RGB uses a single power function:
//   encoded = linear^(1/2.2)
//   linear  = encoded^2.2
//
// Sign-preserving for out-of-range inputs.
//
// Primary source: Adobe Systems Inc., "Adobe RGB (1998) Color Image Encoding"
// (2005).
import { NONLINEAR_TOLERANCE } from '../types.js';
const GAMMA = 2.19921875; // Adobe RGB exact gamma; ≈ 2.2
const INV_GAMMA = 1 / GAMMA;
export function encodeComponent(linear) {
    const abs = Math.abs(linear);
    const sign = Math.sign(linear);
    return sign * Math.pow(abs, INV_GAMMA);
}
export function decodeComponent(encoded) {
    const abs = Math.abs(encoded);
    const sign = Math.sign(encoded);
    return sign * Math.pow(abs, GAMMA);
}
export function encode(linear) {
    return [
        encodeComponent(linear[0]),
        encodeComponent(linear[1]),
        encodeComponent(linear[2]),
    ];
}
export function decode(encoded) {
    return [
        decodeComponent(encoded[0]),
        decodeComponent(encoded[1]),
        decodeComponent(encoded[2]),
    ];
}
export const testVectors = [
    {
        input: [0, 0, 0],
        output: [0, 0, 0],
        tolerance: NONLINEAR_TOLERANCE,
        source: 'Adobe RGB — black point',
    },
    {
        input: [1, 1, 1],
        output: [1, 1, 1],
        tolerance: NONLINEAR_TOLERANCE,
        source: 'Adobe RGB — white point (1^(1/2.2) = 1)',
    },
];
