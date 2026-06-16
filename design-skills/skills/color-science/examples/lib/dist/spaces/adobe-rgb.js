// Linear Adobe RGB (1998) ↔ XYZ_D65
//
// Adobe RGB has wider gamut than sRGB — particularly in greens and cyans.
// Widely used in pro photography and print workflows. White point: D65.
// Transfer: pure 2.2 gamma (see `src/transfer/adobe-rgb.ts`).
//
// Primary source: Adobe Systems Inc., "Adobe RGB (1998) Color Image Encoding"
// (2005). Matrices from Bruce Lindbloom's reference.
import { mulMat3Vec3, xyz, LINEAR_TOLERANCE } from '../types.js';
export const M_XYZ_TO_ADOBE_RGB = [
    [2.0413690, -0.5649464, -0.3446944],
    [-0.9692660, 1.8760108, 0.0415560],
    [0.0134474, -0.1183897, 1.0154096],
];
export const M_ADOBE_RGB_TO_XYZ = [
    [0.5767309, 0.1855540, 0.1881852],
    [0.2973769, 0.6273491, 0.0752741],
    [0.0270343, 0.0706872, 0.9911085],
];
export function toXYZ(c) {
    const [X, Y, Z] = mulMat3Vec3(M_ADOBE_RGB_TO_XYZ, c);
    return xyz(X, Y, Z);
}
export function fromXYZ(c) {
    const [R, G, B] = mulMat3Vec3(M_XYZ_TO_ADOBE_RGB, c);
    return [R, G, B];
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
        output: [1, 1, 1],
        tolerance: 1e-3,
        source: 'D65 white → Adobe RGB (1, 1, 1)',
    },
];
