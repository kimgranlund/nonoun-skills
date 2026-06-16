// Generic color space conversion through the XYZ_D65 hub.
//
// Per ARCHITECTURE.md: every space module exports toXYZ() and fromXYZ().
// Composition is always B.fromXYZ(A.toXYZ(value)) through the hub.
//
// Usage:
//   import * as srgb from './spaces/srgb.js';
//   import * as oklab from './spaces/oklab.js';
//   import { convert } from './convert.js';
//
//   const c_oklab = convert(c_linearSRGB, srgb, oklab);
//
// For chained pipelines (e.g., encoded sRGB → OKLCH for design tokens):
//   import * as srgbTransfer from './transfer/srgb.js';
//   import * as srgb from './spaces/srgb.js';
//   import * as oklab from './spaces/oklab.js';
//   import { convert } from './convert.js';
//
//   const linear = srgbTransfer.decode(encoded);
//   const oklabValue = convert(linear, srgb, oklab);
/**
 * Convert a value from space A to space B by going through XYZ_D65.
 *
 * @param value the color in space A
 * @param from the source space module (must export toXYZ)
 * @param to the destination space module (must export fromXYZ)
 */
export function convert(value, from, to) {
    return to.fromXYZ(from.toXYZ(value));
}
/**
 * Convert any branded color to its XYZ_D65 hub representation.
 * Identity when called on an XYZ_D65 value through `src/spaces/xyz.ts`.
 */
export function toHub(value, from) {
    return from.toXYZ(value);
}
/**
 * Convert an XYZ_D65 hub value into any space.
 */
export function fromHub(xyz, to) {
    return to.fromXYZ(xyz);
}
