// LMS ↔ XYZ_D65
//
// LMS (Long, Medium, Short cone responses) is the linear cone-fundamental
// representation. It's the intermediate space used by OKLab, CIECAM16, and
// other appearance models — but exposing it as a first-class space allows
// direct cone-response work (e.g., chromatic adaptation experiments, custom
// nonlinear transforms).
//
// This module uses **Ottosson's M1 matrix** (the LMS optimization used by
// OKLab). The Smith-Pokorny and CIECAM-style LMS matrices use different
// coefficients; this is one specific LMS basis among several. For broad CIE
// work, the CAT16 matrix from `src/adaptation/bradford.ts` is a related
// alternative.
//
// Primary source: Björn Ottosson 2020 — OKLab paper M1 matrix.
import { mulMat3Vec3, xyz, LINEAR_TOLERANCE } from '../types.js';
/** Ottosson M1: XYZ_D65 → LMS. */
export const M_XYZ_TO_LMS = [
    [0.8189330101, 0.3618667424, -0.1288597137],
    [0.0329845436, 0.9293118715, 0.0361456387],
    [0.0482003018, 0.2643662691, 0.6338517070],
];
/** Ottosson M1 inverse: LMS → XYZ_D65. */
export const M_LMS_TO_XYZ = [
    [1.2270138511, -0.5577999807, 0.2812561490],
    [-0.0405801784, 1.1122568696, -0.0716766787],
    [-0.0763812845, -0.4214819784, 1.5861632204],
];
export function fromXYZ(c) {
    const [L, M, S] = mulMat3Vec3(M_XYZ_TO_LMS, c);
    return [L, M, S];
}
export function toXYZ(c) {
    const [X, Y, Z] = mulMat3Vec3(M_LMS_TO_XYZ, c);
    return xyz(X, Y, Z);
}
export const testVectors = [
    {
        input: xyz(0, 0, 0),
        output: [0, 0, 0],
        tolerance: LINEAR_TOLERANCE,
        source: 'Black point',
    },
    {
        input: xyz(0.9504559270516716, 1.0, 1.0890577507598784),
        output: [1.000, 1.000, 1.000],
        tolerance: 1e-3,
        source: 'D65 white → LMS ≈ (1, 1, 1) (M1 row sums normalize white)',
    },
];
