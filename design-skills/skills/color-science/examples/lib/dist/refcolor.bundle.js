"use strict";
(() => {
  var __defProp = Object.defineProperty;
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };

  // lib/dist/spaces/oklab.js
  var oklab_exports = {};
  __export(oklab_exports, {
    fromXYZ: () => fromXYZ,
    testVectors: () => testVectors,
    toXYZ: () => toXYZ
  });

  // lib/dist/types.js
  var types_exports = {};
  __export(types_exports, {
    LINEAR_TOLERANCE: () => LINEAR_TOLERANCE,
    NONLINEAR_TOLERANCE: () => NONLINEAR_TOLERANCE,
    cbrt: () => cbrt,
    ciecam16_JMh: () => ciecam16_JMh,
    cielab_D65: () => cielab_D65,
    cielch_D65: () => cielch_D65,
    encodedSRGB: () => encodedSRGB,
    hct: () => hct,
    lInfDistance: () => lInfDistance,
    linearP3: () => linearP3,
    linearRec2020: () => linearRec2020,
    linearSRGB: () => linearSRGB,
    mulMat3Mat3: () => mulMat3Mat3,
    mulMat3Vec3: () => mulMat3Vec3,
    okhsl: () => okhsl,
    okhsv: () => okhsv,
    oklab: () => oklab,
    oklch: () => oklch,
    wrapHueDeg: () => wrapHueDeg,
    xyY: () => xyY,
    xyz: () => xyz
  });
  var xyz = (X, Y, Z) => [X, Y, Z];
  var linearSRGB = (R, G2, B4) => [R, G2, B4];
  var encodedSRGB = (R, G2, B4) => [R, G2, B4];
  var linearP3 = (R, G2, B4) => [R, G2, B4];
  var linearRec2020 = (R, G2, B4) => [R, G2, B4];
  var oklab = (L, a, b) => [L, a, b];
  var oklch = (L, C5, h) => [L, C5, h];
  var cielab_D65 = (L, a, b) => [L, a, b];
  var cielch_D65 = (L, C5, h) => [L, C5, h];
  var xyY = (x, y, Y) => [x, y, Y];
  var okhsl = (h, s, l) => [h, s, l];
  var okhsv = (h, s, v) => [h, s, v];
  var hct = (h, c, t) => [h, c, t];
  var ciecam16_JMh = (J, M3, h) => [J, M3, h];
  function mulMat3Vec3(m, v) {
    return [
      m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
      m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
      m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2]
    ];
  }
  function mulMat3Mat3(a, b) {
    const r = (i, j) => a[i][0] * b[0][j] + a[i][1] * b[1][j] + a[i][2] * b[2][j];
    return [
      [r(0, 0), r(0, 1), r(0, 2)],
      [r(1, 0), r(1, 1), r(1, 2)],
      [r(2, 0), r(2, 1), r(2, 2)]
    ];
  }
  var cbrt = (x) => Math.sign(x) * Math.pow(Math.abs(x), 1 / 3);
  var wrapHueDeg = (h) => {
    const r = h % 360;
    return r < 0 ? r + 360 : r;
  };
  var LINEAR_TOLERANCE = 1e-9;
  var NONLINEAR_TOLERANCE = 1e-4;
  function lInfDistance(a, b) {
    return Math.max(Math.abs(a[0] - b[0]), Math.abs(a[1] - b[1]), Math.abs(a[2] - b[2]));
  }

  // lib/dist/spaces/oklab.js
  var M1 = [
    [0.8189330101, 0.3618667424, -0.1288597137],
    [0.0329845436, 0.9293118715, 0.0361456387],
    [0.0482003018, 0.2643662691, 0.633851707]
  ];
  var M1_INV = [
    [1.2270138511, -0.5577999807, 0.281256149],
    [-0.0405801784, 1.1122568696, -0.0716766787],
    [-0.0763812845, -0.4214819784, 1.5861632204]
  ];
  var M2 = [
    [0.2104542553, 0.793617785, -0.0040720468],
    [1.9779984951, -2.428592205, 0.4505937099],
    [0.0259040371, 0.7827717662, -0.808675766]
  ];
  var M2_INV = [
    [1, 0.3963377774, 0.2158037573],
    [1, -0.1055613458, -0.0638541728],
    [1, -0.0894841775, -1.291485548]
  ];
  function fromXYZ(c) {
    const lms = mulMat3Vec3(M1, c);
    const lmsPrime = [
      cbrt(lms[0]),
      cbrt(lms[1]),
      cbrt(lms[2])
    ];
    const [L, a, b] = mulMat3Vec3(M2, lmsPrime);
    return oklab(L, a, b);
  }
  function toXYZ(c) {
    const lmsPrime = mulMat3Vec3(M2_INV, c);
    const lms = [
      lmsPrime[0] ** 3,
      lmsPrime[1] ** 3,
      lmsPrime[2] ** 3
    ];
    const [X, Y, Z] = mulMat3Vec3(M1_INV, lms);
    return xyz(X, Y, Z);
  }
  var testVectors = [
    {
      input: xyz(0.95, 1, 1.089),
      output: oklab(1, 0, 0),
      tolerance: 1e-3,
      source: "Ottosson 2020 \u2014 D65 white point",
      note: "D65 white (Y=1) \u2192 OKLab L=1, a=0, b=0"
    },
    {
      input: xyz(1, 0, 0),
      output: oklab(0.44999, 1.23553, -0.01903),
      tolerance: 1e-3,
      source: "Ottosson 2020 \u2014 pure X stimulus",
      note: "Pure X \u2192 strong red-green axis, near-zero blue-yellow"
    },
    {
      input: xyz(0, 1, 0),
      output: oklab(0.92187, -0.67137, 0.2633),
      tolerance: 1e-3,
      source: "Ottosson 2020 \u2014 pure Y stimulus",
      note: "Pure Y \u2192 negative a (green direction), positive b (yellow direction)"
    },
    {
      input: xyz(0, 0, 1),
      output: oklab(0.15265, -1.41481, -0.4485),
      tolerance: 1e-3,
      source: "Ottosson 2020 \u2014 pure Z stimulus",
      note: "Pure Z \u2192 low L, deep blue direction"
    }
  ];

  // lib/dist/spaces/oklch.js
  var oklch_exports = {};
  __export(oklch_exports, {
    fromOKLab: () => fromOKLab,
    fromXYZ: () => fromXYZ2,
    testVectors: () => testVectors2,
    toOKLab: () => toOKLab,
    toXYZ: () => toXYZ2
  });
  var DEG_TO_RAD = Math.PI / 180;
  var RAD_TO_DEG = 180 / Math.PI;
  function fromOKLab(lab) {
    const [L, a, b] = lab;
    const C5 = Math.sqrt(a * a + b * b);
    let h = Math.atan2(b, a) * RAD_TO_DEG;
    if (h < 0)
      h += 360;
    return oklch(L, C5, h);
  }
  function toOKLab(lch) {
    const [L, C5, hDeg] = lch;
    const h = wrapHueDeg(hDeg) * DEG_TO_RAD;
    return oklab(L, C5 * Math.cos(h), C5 * Math.sin(h));
  }
  function fromXYZ2(c) {
    return fromOKLab(fromXYZ(c));
  }
  function toXYZ2(c) {
    return toXYZ(toOKLab(c));
  }
  var testVectors2 = [
    // Note: achromatic points (C=0) have indeterminate hue. Float noise produces
    // arbitrary hue values that fail strict round-trip. Test vectors below use
    // chromatic inputs where (L, C, h) are all well-defined.
    {
      input: xyz(0.4123907993, 0.2126390059, 0.0193308187),
      // pure sRGB red
      output: oklch(0.6279554, 0.2576, 29.2339),
      tolerance: 0.01,
      source: "OKLab pure sRGB red \u2014 chromatic, hue well-defined"
    }
  ];

  // lib/dist/spaces/cielab.js
  var cielab_exports = {};
  __export(cielab_exports, {
    fromXYZ: () => fromXYZ3,
    testVectors: () => testVectors3,
    toXYZ: () => toXYZ3
  });
  var Xn = 0.9504559270516716;
  var Yn = 1;
  var Zn = 1.0890577507598784;
  var DELTA = 6 / 29;
  var DELTA_CUBED = DELTA * DELTA * DELTA;
  var THREE_DELTA_SQ = 3 * DELTA * DELTA;
  var FOUR_OVER_29 = 4 / 29;
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
  function fromXYZ3(c) {
    const fx = f(c[0] / Xn);
    const fy = f(c[1] / Yn);
    const fz = f(c[2] / Zn);
    return cielab_D65(116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz));
  }
  function toXYZ3(c) {
    const fy = (c[0] + 16) / 116;
    const fx = fy + c[1] / 500;
    const fz = fy - c[2] / 200;
    return xyz(Xn * fInverse(fx), Yn * fInverse(fy), Zn * fInverse(fz));
  }
  var testVectors3 = [
    {
      input: xyz(0, 0, 0),
      output: cielab_D65(0, 0, 0),
      tolerance: NONLINEAR_TOLERANCE,
      source: "CIE 015 \u2014 black point \u2192 L*a*b* (0, 0, 0)"
    },
    {
      input: xyz(Xn, Yn, Zn),
      output: cielab_D65(100, 0, 0),
      tolerance: 1e-6,
      source: "CIE 015 \u2014 D65 white \u2192 L*=100, a*=b*=0"
    },
    {
      input: xyz(Xn * 0.5, Yn * 0.5, Zn * 0.5),
      output: cielab_D65(76.06926101, 0, 0),
      tolerance: NONLINEAR_TOLERANCE,
      source: "CIE 015 \u2014 50% gray (Y=0.5) \u2192 L* \u2248 76.07"
    }
  ];

  // lib/dist/spaces/cielch.js
  var cielch_exports = {};
  __export(cielch_exports, {
    fromCIELAB: () => fromCIELAB,
    fromXYZ: () => fromXYZ4,
    testVectors: () => testVectors4,
    toCIELAB: () => toCIELAB,
    toXYZ: () => toXYZ4
  });
  var DEG_TO_RAD2 = Math.PI / 180;
  var RAD_TO_DEG2 = 180 / Math.PI;
  function fromCIELAB(lab) {
    const [L, a, b] = lab;
    const C5 = Math.sqrt(a * a + b * b);
    let h = Math.atan2(b, a) * RAD_TO_DEG2;
    if (h < 0)
      h += 360;
    return cielch_D65(L, C5, h);
  }
  function toCIELAB(lch) {
    const [L, C5, hDeg] = lch;
    const h = wrapHueDeg(hDeg) * DEG_TO_RAD2;
    return cielab_D65(L, C5 * Math.cos(h), C5 * Math.sin(h));
  }
  function fromXYZ4(c) {
    return fromCIELAB(fromXYZ3(c));
  }
  function toXYZ4(c) {
    return toXYZ3(toCIELAB(c));
  }
  var testVectors4 = [
    {
      input: xyz(0, 0, 0),
      output: cielch_D65(0, 0, 0),
      tolerance: NONLINEAR_TOLERANCE,
      source: "Black point \u2014 L=C=0, hue undefined (returned as 0)"
    },
    {
      input: xyz(0.9504559270516716, 1, 1.0890577507598784),
      output: cielch_D65(100, 0, 0),
      tolerance: 1e-6,
      source: "D65 white \u2192 L*=100, C*=0"
    }
  ];

  // lib/dist/spaces/srgb.js
  var srgb_exports = {};
  __export(srgb_exports, {
    M_SRGB_TO_XYZ: () => M_SRGB_TO_XYZ,
    M_XYZ_TO_SRGB: () => M_XYZ_TO_SRGB,
    fromXYZ: () => fromXYZ5,
    testVectors: () => testVectors5,
    toXYZ: () => toXYZ5
  });
  var M_XYZ_TO_SRGB = [
    [3.2409699419, -1.5373831776, -0.4986107603],
    [-0.9692436363, 1.8759675015, 0.0415550574],
    [0.0556300797, -0.2039769589, 1.0569715142]
  ];
  var M_SRGB_TO_XYZ = [
    [0.4123907993, 0.3575843394, 0.1804807884],
    [0.2126390059, 0.7151686788, 0.0721923154],
    [0.0193308187, 0.1191947798, 0.9505321522]
  ];
  function toXYZ5(c) {
    const [X, Y, Z] = mulMat3Vec3(M_SRGB_TO_XYZ, c);
    return xyz(X, Y, Z);
  }
  function fromXYZ5(c) {
    const [R, G2, B4] = mulMat3Vec3(M_XYZ_TO_SRGB, c);
    return linearSRGB(R, G2, B4);
  }
  var testVectors5 = [
    {
      input: xyz(0, 0, 0),
      output: linearSRGB(0, 0, 0),
      tolerance: LINEAR_TOLERANCE,
      source: "Trivial \u2014 black point"
    },
    {
      input: xyz(0.9504559270516716, 1, 1.0890577507598784),
      output: linearSRGB(1, 1, 1),
      tolerance: 1e-6,
      source: "IEC 61966-2-1 \u2014 D65 white \u2192 linear sRGB (1, 1, 1)"
    },
    {
      input: xyz(0.4123907993, 0.2126390059, 0.0193308187),
      output: linearSRGB(1, 0, 0),
      tolerance: 1e-6,
      source: "IEC 61966-2-1 \u2014 pure red column of M_SRGB_TO_XYZ"
    },
    {
      input: xyz(0.3575843394, 0.7151686788, 0.1191947798),
      output: linearSRGB(0, 1, 0),
      tolerance: 1e-6,
      source: "IEC 61966-2-1 \u2014 pure green column of M_SRGB_TO_XYZ"
    },
    {
      input: xyz(0.1804807884, 0.0721923154, 0.9505321522),
      output: linearSRGB(0, 0, 1),
      tolerance: 1e-6,
      source: "IEC 61966-2-1 \u2014 pure blue column of M_SRGB_TO_XYZ"
    }
  ];

  // lib/dist/spaces/p3.js
  var p3_exports = {};
  __export(p3_exports, {
    M_P3_TO_XYZ: () => M_P3_TO_XYZ,
    M_XYZ_TO_P3: () => M_XYZ_TO_P3,
    fromXYZ: () => fromXYZ6,
    testVectors: () => testVectors6,
    toXYZ: () => toXYZ6
  });
  var M_XYZ_TO_P3 = [
    [2.4934969119, -0.9313836179, -0.4027107845],
    [-0.8294889696, 1.7626640603, 0.0236246858],
    [0.0358458302, -0.0761723893, 0.956884524]
  ];
  var M_P3_TO_XYZ = [
    [0.4865709486, 0.2656676932, 0.1982172852],
    [0.2289745641, 0.6917385241, 0.0792869117],
    [0, 0.0451133819, 1.0439443689]
  ];
  function toXYZ6(c) {
    const [X, Y, Z] = mulMat3Vec3(M_P3_TO_XYZ, c);
    return xyz(X, Y, Z);
  }
  function fromXYZ6(c) {
    const [R, G2, B4] = mulMat3Vec3(M_XYZ_TO_P3, c);
    return linearP3(R, G2, B4);
  }
  var testVectors6 = [
    {
      input: xyz(0, 0, 0),
      output: linearP3(0, 0, 0),
      tolerance: LINEAR_TOLERANCE,
      source: "Trivial \u2014 black point"
    },
    {
      input: xyz(0.9504559270516716, 1, 1.0890577507598784),
      output: linearP3(1, 1, 1),
      tolerance: 1e-6,
      source: "W3C CSS Color 4 \u2014 D65 white \u2192 linear P3 (1, 1, 1)"
    }
  ];

  // lib/dist/spaces/rec2020.js
  var rec2020_exports = {};
  __export(rec2020_exports, {
    M_REC2020_TO_XYZ: () => M_REC2020_TO_XYZ,
    M_XYZ_TO_REC2020: () => M_XYZ_TO_REC2020,
    fromXYZ: () => fromXYZ7,
    testVectors: () => testVectors7,
    toXYZ: () => toXYZ7
  });
  var M_XYZ_TO_REC2020 = [
    [1.716651188, -0.3556707838, -0.2533662814],
    [-0.6666843518, 1.6164812366, 0.0157685458],
    [0.0176398574, -0.0427706133, 0.9421031212]
  ];
  var M_REC2020_TO_XYZ = [
    [0.6369580483, 0.1446169036, 0.1688809752],
    [0.262700212, 0.6779980715, 0.0593017165],
    [0, 0.028072693, 1.0609850577]
  ];
  function toXYZ7(c) {
    const [X, Y, Z] = mulMat3Vec3(M_REC2020_TO_XYZ, c);
    return xyz(X, Y, Z);
  }
  function fromXYZ7(c) {
    const [R, G2, B4] = mulMat3Vec3(M_XYZ_TO_REC2020, c);
    return [R, G2, B4];
  }
  var testVectors7 = [
    {
      input: xyz(0, 0, 0),
      output: [0, 0, 0],
      tolerance: LINEAR_TOLERANCE,
      source: "Trivial \u2014 black point"
    },
    {
      input: xyz(0.9504559270516716, 1, 1.0890577507598784),
      output: [1, 1, 1],
      tolerance: 1e-6,
      source: "W3C CSS Color 4 \u2014 D65 white \u2192 linear Rec.2020 (1, 1, 1)"
    }
  ];

  // lib/dist/spaces/hsl.js
  var hsl_exports = {};
  __export(hsl_exports, {
    fromEncodedSRGB: () => fromEncodedSRGB,
    fromXYZ: () => fromXYZ8,
    testVectors: () => testVectors9,
    toEncodedSRGB: () => toEncodedSRGB,
    toXYZ: () => toXYZ8
  });

  // lib/dist/transfer/srgb.js
  var srgb_exports2 = {};
  __export(srgb_exports2, {
    decode: () => decode,
    decodeComponent: () => decodeComponent,
    encode: () => encode,
    encodeComponent: () => encodeComponent,
    testVectors: () => testVectors8
  });
  function encodeComponent(linear) {
    const abs = Math.abs(linear);
    const sign = Math.sign(linear);
    if (abs <= 31308e-7)
      return sign * 12.92 * abs;
    return sign * (1.055 * Math.pow(abs, 1 / 2.4) - 0.055);
  }
  function decodeComponent(encoded) {
    const abs = Math.abs(encoded);
    const sign = Math.sign(encoded);
    if (abs <= 0.04045)
      return sign * abs / 12.92;
    return sign * Math.pow((abs + 0.055) / 1.055, 2.4);
  }
  function encode(linear) {
    return encodedSRGB(encodeComponent(linear[0]), encodeComponent(linear[1]), encodeComponent(linear[2]));
  }
  function decode(encoded) {
    return linearSRGB(decodeComponent(encoded[0]), decodeComponent(encoded[1]), decodeComponent(encoded[2]));
  }
  var testVectors8 = [
    {
      input: linearSRGB(0, 0, 0),
      output: encodedSRGB(0, 0, 0),
      tolerance: NONLINEAR_TOLERANCE,
      source: "IEC 61966-2-1 \u2014 black point"
    },
    {
      input: linearSRGB(1, 1, 1),
      output: encodedSRGB(1, 1, 1),
      tolerance: NONLINEAR_TOLERANCE,
      source: "IEC 61966-2-1 \u2014 white point (1.055 * 1^(1/2.4) - 0.055 = 1)"
    },
    {
      input: linearSRGB(0.5, 0.5, 0.5),
      output: encodedSRGB(0.7353569830524495, 0.7353569830524495, 0.7353569830524495),
      tolerance: NONLINEAR_TOLERANCE,
      source: "Linear 0.5 \u2192 encoded ~0.735 (canonical 50% linear gray)"
    },
    {
      input: linearSRGB(31308e-7, 31308e-7, 31308e-7),
      output: encodedSRGB(0.04045, 0.04045, 0.04045),
      tolerance: NONLINEAR_TOLERANCE,
      source: "IEC 61966-2-1 \u2014 piecewise boundary (12.92 \xD7 0.0031308 = 0.04045)"
    }
  ];

  // lib/dist/spaces/hsl.js
  function toEncodedSRGB(hsl) {
    const [hDeg, s, l] = hsl;
    const h = wrapHueDeg(hDeg);
    const c = (1 - Math.abs(2 * l - 1)) * s;
    const hp = h / 60;
    const x = c * (1 - Math.abs(hp % 2 - 1));
    let r1 = 0, g1 = 0, b1 = 0;
    if (hp < 1) {
      r1 = c;
      g1 = x;
      b1 = 0;
    } else if (hp < 2) {
      r1 = x;
      g1 = c;
      b1 = 0;
    } else if (hp < 3) {
      r1 = 0;
      g1 = c;
      b1 = x;
    } else if (hp < 4) {
      r1 = 0;
      g1 = x;
      b1 = c;
    } else if (hp < 5) {
      r1 = x;
      g1 = 0;
      b1 = c;
    } else {
      r1 = c;
      g1 = 0;
      b1 = x;
    }
    const m = l - c / 2;
    return encodedSRGB(r1 + m, g1 + m, b1 + m);
  }
  function fromEncodedSRGB(rgb) {
    const [r, g, b] = rgb;
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const d = max - min;
    const l = (max + min) / 2;
    let h;
    let s;
    if (d === 0) {
      h = 0;
      s = 0;
    } else {
      s = d / (1 - Math.abs(2 * l - 1));
      if (max === r)
        h = 60 * ((g - b) / d % 6);
      else if (max === g)
        h = 60 * ((b - r) / d + 2);
      else
        h = 60 * ((r - g) / d + 4);
      if (h < 0)
        h += 360;
    }
    return [h, s, l];
  }
  function toXYZ8(hsl) {
    const encoded = toEncodedSRGB(hsl);
    const linear = decode(encoded);
    return toXYZ5(linear);
  }
  function fromXYZ8(c) {
    const linear = fromXYZ5(c);
    const encoded = encode(linear);
    return fromEncodedSRGB(encoded);
  }
  var testVectors9 = [
    // Note: achromatic round-trip fails because hue is indeterminate at S=0.
    // Only chromatic test vectors where (h, s, l) are all well-defined.
    {
      input: xyz(0.4123907993, 0.2126390059, 0.0193308187),
      // pure sRGB red
      output: [0, 1, 0.5],
      tolerance: 1e-3,
      source: "Pure sRGB red \u2192 HSL (0\xB0, 100%, 50%)"
    }
  ];

  // lib/dist/spaces/hsv.js
  var hsv_exports = {};
  __export(hsv_exports, {
    fromEncodedSRGB: () => fromEncodedSRGB2,
    fromXYZ: () => fromXYZ9,
    testVectors: () => testVectors10,
    toEncodedSRGB: () => toEncodedSRGB2,
    toXYZ: () => toXYZ9
  });
  function toEncodedSRGB2(hsv) {
    const [hDeg, s, v] = hsv;
    const h = wrapHueDeg(hDeg);
    const c = v * s;
    const hp = h / 60;
    const x = c * (1 - Math.abs(hp % 2 - 1));
    let r1 = 0, g1 = 0, b1 = 0;
    if (hp < 1) {
      r1 = c;
      g1 = x;
      b1 = 0;
    } else if (hp < 2) {
      r1 = x;
      g1 = c;
      b1 = 0;
    } else if (hp < 3) {
      r1 = 0;
      g1 = c;
      b1 = x;
    } else if (hp < 4) {
      r1 = 0;
      g1 = x;
      b1 = c;
    } else if (hp < 5) {
      r1 = x;
      g1 = 0;
      b1 = c;
    } else {
      r1 = c;
      g1 = 0;
      b1 = x;
    }
    const m = v - c;
    return encodedSRGB(r1 + m, g1 + m, b1 + m);
  }
  function fromEncodedSRGB2(rgb) {
    const [r, g, b] = rgb;
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const d = max - min;
    const v = max;
    const s = max === 0 ? 0 : d / max;
    let h;
    if (d === 0) {
      h = 0;
    } else if (max === r) {
      h = 60 * ((g - b) / d % 6);
    } else if (max === g) {
      h = 60 * ((b - r) / d + 2);
    } else {
      h = 60 * ((r - g) / d + 4);
    }
    if (h < 0)
      h += 360;
    return [h, s, v];
  }
  function toXYZ9(hsv) {
    return toXYZ5(decode(toEncodedSRGB2(hsv)));
  }
  function fromXYZ9(c) {
    return fromEncodedSRGB2(encode(fromXYZ5(c)));
  }
  var testVectors10 = [
    // Note: achromatic round-trip fails because hue is indeterminate at S=0.
    // Only chromatic test vectors below.
    {
      input: xyz(0.4123907993, 0.2126390059, 0.0193308187),
      // pure sRGB red
      output: [0, 1, 1],
      tolerance: 1e-3,
      source: "Pure sRGB red \u2192 HSV (0\xB0, 100%, 100%)"
    }
  ];

  // lib/dist/spaces/hct.js
  var hct_exports = {};
  __export(hct_exports, {
    fromXYZ: () => fromXYZ11,
    testVectors: () => testVectors12,
    toXYZ: () => toXYZ11
  });

  // lib/dist/spaces/ciecam16.js
  var ciecam16_exports = {};
  __export(ciecam16_exports, {
    DEFAULT_VC: () => DEFAULT_VC,
    fromXYZ: () => fromXYZ10,
    testVectors: () => testVectors11,
    toXYZ: () => toXYZ10
  });
  var M_CAT16 = [
    [0.401288, 0.650173, -0.051461],
    [-0.250268, 1.204414, 0.045854],
    [-2079e-6, 0.048952, 0.953127]
  ];
  var M_CAT16_INV = [
    [1.86206786, -1.01125463, 0.14918677],
    [0.38752654, 0.62144744, -897398e-8],
    [-0.0158415, -0.03412294, 1.04996444]
  ];
  var Y_AT_LSTAR_50 = 18.41835828999998;
  var DEFAULT_VC = {
    whitePointXYZ: [95.04559270516717, 100, 108.90577507598783],
    adaptingLuminance: 200 / Math.PI * Y_AT_LSTAR_50 / 100,
    backgroundLstar: 50,
    surround: 2,
    discountingIlluminant: false
  };
  function precompute(vc) {
    const [Xw, Yw, Zw] = vc.whitePointXYZ;
    const rgbW = mulMat3Vec3(M_CAT16, [Xw, Yw, Zw]);
    const f2 = vc.surround === 0 ? 0.8 : vc.surround === 1 ? 0.9 : 1;
    const c = vc.surround === 0 ? 0.525 : vc.surround === 1 ? 0.59 : 0.69;
    const nc = c === 0.525 ? 0.8 : c === 0.59 ? 0.9 : 1;
    const dRaw = f2 * (1 - 1 / 3.6 * Math.exp((-vc.adaptingLuminance - 42) / 92));
    const d = vc.discountingIlluminant ? 1 : Math.max(0, Math.min(1, dRaw));
    const rgbD = [
      d * (100 / rgbW[0]) + 1 - d,
      d * (100 / rgbW[1]) + 1 - d,
      d * (100 / rgbW[2]) + 1 - d
    ];
    const k = 1 / (5 * vc.adaptingLuminance + 1);
    const k4 = k * k * k * k;
    const k4_1 = 1 - k4;
    const fl = k4 * vc.adaptingLuminance + 0.1 * k4_1 * k4_1 * Math.cbrt(5 * vc.adaptingLuminance);
    const flRoot = Math.pow(fl, 0.25);
    const yFromLstar2 = (L) => {
      const fy = (L + 16) / 116;
      const delta = 6 / 29;
      return fy > delta ? fy ** 3 * 100 : 3 * delta * delta * (fy - 4 / 29) * 100;
    };
    const yb = yFromLstar2(vc.backgroundLstar);
    const n = yb / Yw;
    const nbb = 0.725 * Math.pow(1 / n, 0.2);
    const ncb = nbb;
    const rgbAW = [
      rgbD[0] * rgbW[0],
      rgbD[1] * rgbW[1],
      rgbD[2] * rgbW[2]
    ];
    const rgbAfW = [
      adaptResponse(rgbAW[0], fl),
      adaptResponse(rgbAW[1], fl),
      adaptResponse(rgbAW[2], fl)
    ];
    const aw = (2 * rgbAfW[0] + rgbAfW[1] + 0.05 * rgbAfW[2]) * nbb;
    const z = 1.48 + Math.sqrt(n);
    return { vc, n, aw, nbb, ncb, c, nc, rgbD, fl, flRoot, z };
  }
  function adaptResponse(component, fl) {
    const sign = Math.sign(component);
    const abs = Math.abs(component);
    const x = Math.pow(fl * abs / 100, 0.42);
    return sign * 400 * x / (x + 27.13);
  }
  function unadaptResponse(value, fl) {
    const sign = Math.sign(value);
    const abs = Math.abs(value);
    const denom = Math.max(0, 400 - abs);
    if (denom === 0)
      return 0;
    return sign * (100 / fl) * Math.pow(27.13 * abs / denom, 1 / 0.42);
  }
  function fromXYZ10(c, pre = precompute(DEFAULT_VC)) {
    const X100 = c[0] * 100, Y100 = c[1] * 100, Z100 = c[2] * 100;
    const rgb = mulMat3Vec3(M_CAT16, [X100, Y100, Z100]);
    const rgbAdapted = [
      pre.rgbD[0] * rgb[0],
      pre.rgbD[1] * rgb[1],
      pre.rgbD[2] * rgb[2]
    ];
    const rgbAf = [
      adaptResponse(rgbAdapted[0], pre.fl),
      adaptResponse(rgbAdapted[1], pre.fl),
      adaptResponse(rgbAdapted[2], pre.fl)
    ];
    const a = rgbAf[0] - 12 * rgbAf[1] / 11 + rgbAf[2] / 11;
    const b = (rgbAf[0] + rgbAf[1] - 2 * rgbAf[2]) / 9;
    let hRad = Math.atan2(b, a);
    let hDeg = hRad * (180 / Math.PI);
    if (hDeg < 0)
      hDeg += 360;
    const eccentricity = 0.25 * (Math.cos(hRad + 2) + 3.8);
    const achromaticResponse = (2 * rgbAf[0] + rgbAf[1] + 0.05 * rgbAf[2]) * pre.nbb;
    const Jbase = Math.max(0, achromaticResponse / pre.aw);
    const J = 100 * Math.pow(Jbase, pre.c * pre.z);
    const t = 5e4 / 13 * pre.nc * pre.ncb * eccentricity * Math.sqrt(a * a + b * b) / (rgbAf[0] + rgbAf[1] + 21 * rgbAf[2] / 20);
    const alpha = Math.pow(t, 0.9) * Math.pow(1.64 - Math.pow(0.29, pre.n), 0.73);
    const C5 = alpha * Math.sqrt(J / 100);
    const M3 = C5 * pre.flRoot;
    return ciecam16_JMh(J, M3, hDeg);
  }
  function toXYZ10(jmh, pre = precompute(DEFAULT_VC)) {
    const [J, M3, hDeg] = jmh;
    const h = wrapHueDeg(hDeg);
    const hRad = h * (Math.PI / 180);
    const alpha = M3 / pre.flRoot / Math.sqrt(Math.max(J, 1e-12) / 100);
    const t = Math.pow(alpha / Math.pow(1.64 - Math.pow(0.29, pre.n), 0.73), 1 / 0.9);
    const eccentricity = 0.25 * (Math.cos(hRad + 2) + 3.8);
    const A5 = pre.aw * Math.pow(J / 100, 1 / (pre.c * pre.z));
    const p1 = 5e4 / 13 * pre.nc * pre.ncb * eccentricity;
    const p2 = A5 / pre.nbb;
    const hSin = Math.sin(hRad);
    const hCos = Math.cos(hRad);
    const gamma = 23 * (p2 + 0.305) * t / (23 * p1 + 11 * t * hCos + 108 * t * hSin);
    const a = gamma * hCos;
    const b = gamma * hSin;
    const rA = (460 * p2 + 451 * a + 288 * b) / 1403;
    const gA = (460 * p2 - 891 * a - 261 * b) / 1403;
    const bA = (460 * p2 - 220 * a - 6300 * b) / 1403;
    const rC = unadaptResponse(rA, pre.fl);
    const gC = unadaptResponse(gA, pre.fl);
    const bC = unadaptResponse(bA, pre.fl);
    const rUnadapted = rC / pre.rgbD[0];
    const gUnadapted = gC / pre.rgbD[1];
    const bUnadapted = bC / pre.rgbD[2];
    const [X100, Y100, Z100] = mulMat3Vec3(M_CAT16_INV, [rUnadapted, gUnadapted, bUnadapted]);
    return xyz(X100 / 100, Y100 / 100, Z100 / 100);
  }
  var testVectors11 = [
    {
      input: xyz(0, 0, 0),
      output: ciecam16_JMh(0, 0, 0),
      tolerance: 1e-3,
      source: "Black point \u2014 J=M=0, hue indeterminate (atan2(0,0)=0)"
    }
  ];

  // lib/dist/spaces/hct.js
  function fromXYZ11(c) {
    const cam = fromXYZ10(c);
    const lab = fromXYZ3(c);
    return hct(cam[2], cam[1], lab[0]);
  }
  var DELTA2 = 6 / 29;
  var FOUR_OVER_292 = 4 / 29;
  var THREE_DELTA_SQ2 = 3 * DELTA2 * DELTA2;
  function yFromLstar(L) {
    const fy = (L + 16) / 116;
    return fy > DELTA2 ? fy * fy * fy : THREE_DELTA_SQ2 * (fy - FOUR_OVER_292);
  }
  function toXYZ11(c) {
    const [H, C5, T] = c;
    if (C5 === 0 || T === 0 || T === 100) {
      return toXYZ3(cielab_D65(T, 0, 0));
    }
    const Y_target = yFromLstar(T);
    let J = T;
    let Xout = 0, Yout = 0, Zout = 0;
    for (let i = 0; i < 8; i++) {
      const xyzCandidate = toXYZ10(ciecam16_JMh(J, C5, wrapHueDeg(H)));
      Xout = xyzCandidate[0];
      Yout = xyzCandidate[1];
      Zout = xyzCandidate[2];
      const Y_actual = Yout;
      if (Math.abs(Y_actual - Y_target) < 1e-6)
        break;
      if (Y_actual === 0)
        break;
      J *= Y_target / Y_actual;
      J = Math.max(1e-6, Math.min(100, J));
    }
    return xyz(Xout, Yout, Zout);
  }
  var testVectors12 = [
    {
      input: xyz(0, 0, 0),
      output: hct(0, 0, 0),
      tolerance: 1e-3,
      source: "Black \u2192 HCT (0, 0, 0) \u2014 achromatic, hue irrelevant"
    }
    // Note: D65 white produces ~2.3 residual chroma under partial chromatic adaptation
    // (discountingIlluminant: false). This is mathematically correct for CIECAM16 but
    // differs from Material's HCT solver, which biases toward 0 for near-achromatic
    // inputs. For Material-faithful behavior, set `discountingIlluminant: true` in the
    // viewing conditions or use a gamut-aware HCT solver (TODO: `src/gamut/hct-solver.ts`).
  ];

  // lib/dist/spaces/cam16-ucs.js
  var cam16_ucs_exports = {};
  __export(cam16_ucs_exports, {
    deltaECAM16: () => deltaECAM16,
    fromJMh: () => fromJMh,
    fromXYZ: () => fromXYZ12,
    testVectors: () => testVectors13,
    toJMh: () => toJMh,
    toXYZ: () => toXYZ12
  });
  var C1 = 7e-3;
  var C2 = 0.0228;
  var DEG_TO_RAD3 = Math.PI / 180;
  var RAD_TO_DEG3 = 180 / Math.PI;
  function fromJMh(jmh) {
    const [J, M3, hDeg] = jmh;
    const Jp = (1 + 100 * C1) * J / (1 + C1 * J);
    const Mp = 1 / C2 * Math.log(1 + C2 * M3);
    const hRad = wrapHueDeg(hDeg) * DEG_TO_RAD3;
    return [Jp, Mp * Math.cos(hRad), Mp * Math.sin(hRad)];
  }
  function toJMh(ucs) {
    const [Jp, ap, bp] = ucs;
    const J = Jp / (1 + C1 * (100 - Jp));
    const Mp = Math.sqrt(ap * ap + bp * bp);
    const M3 = (Math.exp(C2 * Mp) - 1) / C2;
    let hDeg = Math.atan2(bp, ap) * RAD_TO_DEG3;
    if (hDeg < 0)
      hDeg += 360;
    return [J, M3, hDeg];
  }
  function fromXYZ12(c) {
    return fromJMh(fromXYZ10(c));
  }
  function toXYZ12(c) {
    return toXYZ10(toJMh(c));
  }
  function deltaECAM16(a, b) {
    const dJ = a[0] - b[0];
    const dA = a[1] - b[1];
    const dB = a[2] - b[2];
    return Math.sqrt(dJ * dJ + dA * dA + dB * dB);
  }
  var testVectors13 = [
    {
      input: xyz(0, 0, 0),
      output: [0, 0, 0],
      tolerance: 1e-3,
      source: "Black point under default viewing conditions"
    }
  ];

  // lib/dist/spaces/jzazbz.js
  var jzazbz_exports = {};
  __export(jzazbz_exports, {
    fromXYZ: () => fromXYZ13,
    testVectors: () => testVectors14,
    toXYZ: () => toXYZ13
  });
  var B = 1.15;
  var G = 0.66;
  var N = 2610 / 16384;
  var M = 1.7 * 2523 / 32;
  var C12 = 3424 / 4096;
  var C22 = 2413 / 128;
  var C3 = 2392 / 128;
  var D_J = -0.56;
  var D0 = 16295499532821565e-27;
  var M12 = [
    [0.41478972, 0.579999, 0.014648],
    [-0.20151, 1.120649, 0.0531008],
    [-0.0166008, 0.2648, 0.6684799]
  ];
  var M22 = [
    [0.5, 0.5, 0],
    [3.524, -4.066708, 0.542708],
    [0.199076, 1.096799, -1.295875]
  ];
  var M1_INV2 = [
    [1.9242264358, -1.0047923126, 0.037651404],
    [0.3503167621, 0.7264811939, -0.0653844229],
    [-0.090982811, -0.3127282905, 1.5227665613]
  ];
  var M2_INV2 = [
    [1, 0.1386050432, 0.0580473162],
    [1, -0.1386050432, -0.0580473162],
    [1, -0.0960192421, -0.811891896]
  ];
  function pqLike(x) {
    const xp = Math.pow(Math.max(x, 0) / 1e4, N);
    return Math.pow((C12 + C22 * xp) / (1 + C3 * xp), M);
  }
  function pqLikeInverse(y) {
    const yp = Math.pow(Math.max(y, 0), 1 / M);
    const num = C12 - yp;
    const den = C3 * yp - C22;
    return 1e4 * Math.pow(num / den, 1 / N);
  }
  function fromXYZ13(c) {
    const X = c[0] * 1e4;
    const Y = c[1] * 1e4;
    const Z = c[2] * 1e4;
    const Xp = B * X - (B - 1) * Z;
    const Yp = G * Y - (G - 1) * X;
    const lms = mulMat3Vec3(M12, [Xp, Yp, Z]);
    const lmsP = [pqLike(lms[0]), pqLike(lms[1]), pqLike(lms[2])];
    const [Iz, az, bz] = mulMat3Vec3(M22, lmsP);
    const Jz = (1 + D_J) * Iz / (1 + D_J * Iz) - D0;
    return [Jz, az, bz];
  }
  function toXYZ13(c) {
    const [Jz, az, bz] = c;
    const JzPlusD0 = Jz + D0;
    const Iz = JzPlusD0 / (1 + D_J - D_J * JzPlusD0);
    const lmsP = mulMat3Vec3(M2_INV2, [Iz, az, bz]);
    const lms = [pqLikeInverse(lmsP[0]), pqLikeInverse(lmsP[1]), pqLikeInverse(lmsP[2])];
    const [Xp, Yp, Z] = mulMat3Vec3(M1_INV2, lms);
    const X = (Xp + (B - 1) * Z) / B;
    const Y = (Yp + (G - 1) * X) / G;
    return xyz(X / 1e4, Y / 1e4, Z / 1e4);
  }
  var testVectors14 = [
    {
      input: xyz(0, 0, 0),
      output: [0 - D0, 0, 0],
      tolerance: 1e-3,
      source: "Black point \u2014 Jz = -D0 \u2248 0, az = bz = 0"
    }
  ];

  // lib/dist/spaces/xyy.js
  var xyy_exports = {};
  __export(xyy_exports, {
    fromXYZ: () => fromXYZ14,
    testVectors: () => testVectors15,
    toXYZ: () => toXYZ14
  });
  function fromXYZ14(c) {
    const [X, Y, Z] = c;
    const sum = X + Y + Z;
    if (sum === 0) {
      return xyY(0.31272, 0.32903, 0);
    }
    return xyY(X / sum, Y / sum, Y);
  }
  function toXYZ14(c) {
    const [x, y, Y] = c;
    if (y === 0)
      return xyz(0, 0, 0);
    const X = x * Y / y;
    const Z = (1 - x - y) * Y / y;
    return xyz(X, Y, Z);
  }
  var testVectors15 = [
    {
      input: xyz(0.9504559270516716, 1, 1.0890577507598784),
      output: xyY(0.31272661468101587, 0.32902313032606195, 1),
      tolerance: 1e-4,
      source: "D65 white point \u2014 canonical chromaticity x\u22480.3127, y\u22480.3290"
    },
    {
      input: xyz(0, 0, 0),
      output: xyY(0.31272, 0.32903, 0),
      tolerance: 1e-3,
      source: "Black point \u2014 chromaticity convention (D65 fallback)"
    }
  ];

  // lib/dist/spaces/xyz.js
  var xyz_exports = {};
  __export(xyz_exports, {
    fromXYZ: () => fromXYZ15,
    testVectors: () => testVectors16,
    toXYZ: () => toXYZ15
  });
  function toXYZ15(c) {
    return c;
  }
  function fromXYZ15(c) {
    return c;
  }
  var testVectors16 = [
    {
      input: xyz(0.95047, 1, 1.08883),
      output: xyz(0.95047, 1, 1.08883),
      tolerance: LINEAR_TOLERANCE,
      source: "D65 white point \u2014 identity check"
    }
  ];

  // lib/dist/transfer/rec2020.js
  var rec2020_exports2 = {};
  __export(rec2020_exports2, {
    decode: () => decode2,
    decodeComponent: () => decodeComponent2,
    encode: () => encode2,
    encodeComponent: () => encodeComponent2,
    testVectors: () => testVectors17
  });
  var ALPHA = 1.09929682680944;
  var BETA = 0.018053968510807;
  function encodeComponent2(linear) {
    const abs = Math.abs(linear);
    const sign = Math.sign(linear);
    if (abs < BETA)
      return sign * 4.5 * abs;
    return sign * (ALPHA * Math.pow(abs, 0.45) - (ALPHA - 1));
  }
  function decodeComponent2(encoded) {
    const abs = Math.abs(encoded);
    const sign = Math.sign(encoded);
    if (abs < BETA * 4.5)
      return sign * abs / 4.5;
    return sign * Math.pow((abs + (ALPHA - 1)) / ALPHA, 1 / 0.45);
  }
  function encode2(linear) {
    return [
      encodeComponent2(linear[0]),
      encodeComponent2(linear[1]),
      encodeComponent2(linear[2])
    ];
  }
  function decode2(encoded) {
    return [
      decodeComponent2(encoded[0]),
      decodeComponent2(encoded[1]),
      decodeComponent2(encoded[2])
    ];
  }
  var testVectors17 = [
    {
      input: [0, 0, 0],
      output: [0, 0, 0],
      tolerance: NONLINEAR_TOLERANCE,
      source: "BT.2020 \u2014 black point"
    },
    {
      input: [1, 1, 1],
      output: [1, 1, 1],
      tolerance: NONLINEAR_TOLERANCE,
      source: "BT.2020 \u2014 white point"
    }
  ];

  // lib/dist/transfer/pq.js
  var pq_exports = {};
  __export(pq_exports, {
    decode: () => decode3,
    decodeComponent: () => decodeComponent3,
    decodeNits: () => decodeNits,
    encode: () => encode3,
    encodeComponent: () => encodeComponent3,
    encodeNits: () => encodeNits,
    testVectors: () => testVectors18
  });
  var M13 = 2610 / 16384;
  var M23 = 2523 / 4096 * 128;
  var C13 = 3424 / 4096;
  var C23 = 2413 / 4096 * 32;
  var C32 = 2392 / 4096 * 32;
  function encodeComponent3(linear) {
    const Y = Math.max(0, linear);
    const Yp = Math.pow(Y, M13);
    return Math.pow((C13 + C23 * Yp) / (1 + C32 * Yp), M23);
  }
  function decodeComponent3(encoded) {
    const E3 = Math.max(0, encoded);
    const Ep = Math.pow(E3, 1 / M23);
    const num = Math.max(0, Ep - C13);
    const den = Math.max(1e-12, C23 - C32 * Ep);
    return Math.pow(num / den, 1 / M13);
  }
  function encode3(linear) {
    return [encodeComponent3(linear[0]), encodeComponent3(linear[1]), encodeComponent3(linear[2])];
  }
  function decode3(encoded) {
    return [decodeComponent3(encoded[0]), decodeComponent3(encoded[1]), decodeComponent3(encoded[2])];
  }
  var encodeNits = (nits) => encodeComponent3(nits / 1e4);
  var decodeNits = (encoded) => decodeComponent3(encoded) * 1e4;
  var testVectors18 = [
    {
      input: [0, 0, 0],
      output: [0, 0, 0],
      tolerance: NONLINEAR_TOLERANCE,
      source: "SMPTE ST 2084 \u2014 black point"
    },
    {
      input: [1, 1, 1],
      output: [1, 1, 1],
      tolerance: NONLINEAR_TOLERANCE,
      source: "SMPTE ST 2084 \u2014 peak (10,000 nits)"
    }
  ];

  // lib/dist/transfer/hlg.js
  var hlg_exports = {};
  __export(hlg_exports, {
    decode: () => decode4,
    decodeComponent: () => decodeComponent4,
    encode: () => encode4,
    encodeComponent: () => encodeComponent4,
    testVectors: () => testVectors19
  });
  var A = 0.17883277;
  var B2 = 0.28466892;
  var C = 0.55991073;
  function encodeComponent4(linear) {
    const L = Math.max(0, linear);
    if (L <= 1 / 12)
      return Math.sqrt(3 * L);
    return A * Math.log(12 * L - B2) + C;
  }
  function decodeComponent4(encoded) {
    const V = Math.max(0, encoded);
    if (V <= 0.5)
      return V * V / 3;
    return (Math.exp((V - C) / A) + B2) / 12;
  }
  function encode4(linear) {
    return [encodeComponent4(linear[0]), encodeComponent4(linear[1]), encodeComponent4(linear[2])];
  }
  function decode4(encoded) {
    return [decodeComponent4(encoded[0]), decodeComponent4(encoded[1]), decodeComponent4(encoded[2])];
  }
  var testVectors19 = [
    {
      input: [0, 0, 0],
      output: [0, 0, 0],
      tolerance: NONLINEAR_TOLERANCE,
      source: "BT.2100 HLG \u2014 black point"
    },
    {
      input: [1 / 12, 1 / 12, 1 / 12],
      output: [0.5, 0.5, 0.5],
      tolerance: NONLINEAR_TOLERANCE,
      source: "BT.2100 HLG \u2014 piecewise boundary at 1/12 linear \u2192 0.5 encoded"
    },
    {
      input: [1, 1, 1],
      output: [1, 1, 1],
      tolerance: NONLINEAR_TOLERANCE,
      source: "BT.2100 HLG \u2014 reference white"
    }
  ];

  // lib/dist/transfer/adobe-rgb.js
  var adobe_rgb_exports = {};
  __export(adobe_rgb_exports, {
    decode: () => decode5,
    decodeComponent: () => decodeComponent5,
    encode: () => encode5,
    encodeComponent: () => encodeComponent5,
    testVectors: () => testVectors20
  });
  var GAMMA = 2.19921875;
  var INV_GAMMA = 1 / GAMMA;
  function encodeComponent5(linear) {
    const abs = Math.abs(linear);
    const sign = Math.sign(linear);
    return sign * Math.pow(abs, INV_GAMMA);
  }
  function decodeComponent5(encoded) {
    const abs = Math.abs(encoded);
    const sign = Math.sign(encoded);
    return sign * Math.pow(abs, GAMMA);
  }
  function encode5(linear) {
    return [
      encodeComponent5(linear[0]),
      encodeComponent5(linear[1]),
      encodeComponent5(linear[2])
    ];
  }
  function decode5(encoded) {
    return [
      decodeComponent5(encoded[0]),
      decodeComponent5(encoded[1]),
      decodeComponent5(encoded[2])
    ];
  }
  var testVectors20 = [
    {
      input: [0, 0, 0],
      output: [0, 0, 0],
      tolerance: NONLINEAR_TOLERANCE,
      source: "Adobe RGB \u2014 black point"
    },
    {
      input: [1, 1, 1],
      output: [1, 1, 1],
      tolerance: NONLINEAR_TOLERANCE,
      source: "Adobe RGB \u2014 white point (1^(1/2.2) = 1)"
    }
  ];

  // lib/dist/transfer/prophoto.js
  var prophoto_exports = {};
  __export(prophoto_exports, {
    decode: () => decode6,
    decodeComponent: () => decodeComponent6,
    encode: () => encode6,
    encodeComponent: () => encodeComponent6,
    testVectors: () => testVectors21
  });
  var ET = 1 / 512;
  var ET2 = 16 / 512;
  var SLOPE = 16;
  var GAMMA2 = 1.8;
  var INV_GAMMA2 = 1 / GAMMA2;
  function encodeComponent6(linear) {
    const abs = Math.abs(linear);
    const sign = Math.sign(linear);
    if (abs < ET)
      return sign * SLOPE * abs;
    return sign * Math.pow(abs, INV_GAMMA2);
  }
  function decodeComponent6(encoded) {
    const abs = Math.abs(encoded);
    const sign = Math.sign(encoded);
    if (abs < ET2)
      return sign * abs / SLOPE;
    return sign * Math.pow(abs, GAMMA2);
  }
  function encode6(linear) {
    return [
      encodeComponent6(linear[0]),
      encodeComponent6(linear[1]),
      encodeComponent6(linear[2])
    ];
  }
  function decode6(encoded) {
    return [
      decodeComponent6(encoded[0]),
      decodeComponent6(encoded[1]),
      decodeComponent6(encoded[2])
    ];
  }
  var testVectors21 = [
    {
      input: [0, 0, 0],
      output: [0, 0, 0],
      tolerance: NONLINEAR_TOLERANCE,
      source: "ProPhoto \u2014 black point"
    },
    {
      input: [1, 1, 1],
      output: [1, 1, 1],
      tolerance: NONLINEAR_TOLERANCE,
      source: "ProPhoto \u2014 white point (1^(1/1.8) = 1)"
    },
    {
      input: [ET, ET, ET],
      output: [ET2, ET2, ET2],
      tolerance: NONLINEAR_TOLERANCE,
      source: "ProPhoto \u2014 piecewise boundary at linear=1/512"
    }
  ];

  // lib/dist/metrics/luminance.js
  var luminance_exports = {};
  __export(luminance_exports, {
    fromEncodedSRGB: () => fromEncodedSRGB3,
    fromLinearSRGB: () => fromLinearSRGB,
    fromXYZ: () => fromXYZ16,
    passesAA: () => passesAA,
    passesAAA: () => passesAAA,
    passesAALarge: () => passesAALarge,
    testCases: () => testCases,
    wcagContrast: () => wcagContrast
  });
  function fromXYZ16(c) {
    return c[1];
  }
  function fromLinearSRGB(c) {
    return 0.2126390059 * c[0] + 0.7151686788 * c[1] + 0.0721923154 * c[2];
  }
  function fromEncodedSRGB3(c) {
    return fromLinearSRGB(decode(c));
  }
  function wcagContrast(a, b) {
    const La = fromEncodedSRGB3(a);
    const Lb = fromEncodedSRGB3(b);
    const lighter = Math.max(La, Lb);
    const darker = Math.min(La, Lb);
    return (lighter + 0.05) / (darker + 0.05);
  }
  var passesAA = (a, b) => wcagContrast(a, b) >= 4.5;
  var passesAALarge = (a, b) => wcagContrast(a, b) >= 3;
  var passesAAA = (a, b) => wcagContrast(a, b) >= 7;
  var testCases = [
    {
      name: "luminance.fromXYZ extracts Y component",
      fn: () => fromXYZ16(xyz(0.5, 0.7, 0.3)),
      expected: 0.7,
      tolerance: 1e-12,
      source: "Y is the second component of XYZ_D65 by definition"
    },
    {
      name: "linear sRGB white has Y = 1",
      fn: () => fromLinearSRGB(linearSRGB(1, 1, 1)),
      expected: 1,
      tolerance: 1e-6,
      source: "BT.709 luminance coefficients sum to 1"
    },
    {
      name: "linear sRGB black has Y = 0",
      fn: () => fromLinearSRGB(linearSRGB(0, 0, 0)),
      expected: 0,
      tolerance: 1e-12,
      source: "Zero light \u2192 zero luminance"
    },
    {
      name: "WCAG contrast pure white on pure black = 21",
      fn: () => wcagContrast(encodedSRGB(1, 1, 1), encodedSRGB(0, 0, 0)),
      expected: 21,
      tolerance: 1e-4,
      source: "WCAG max contrast: (1 + 0.05) / (0 + 0.05) = 21"
    },
    {
      name: "WCAG contrast same color = 1",
      fn: () => wcagContrast(encodedSRGB(0.5, 0.5, 0.5), encodedSRGB(0.5, 0.5, 0.5)),
      expected: 1,
      tolerance: 1e-12,
      source: "WCAG min contrast: identity is 1"
    },
    {
      name: "WCAG contrast is symmetric",
      fn: () => {
        const a = encodedSRGB(0.2, 0.3, 0.4);
        const b = encodedSRGB(0.8, 0.7, 0.6);
        return Math.abs(wcagContrast(a, b) - wcagContrast(b, a));
      },
      expected: 0,
      tolerance: 1e-12,
      source: "WCAG contrast is order-independent"
    }
  ];

  // lib/dist/metrics/apca.js
  var apca_exports = {};
  __export(apca_exports, {
    apcaContrast: () => apcaContrast,
    apcaY: () => apcaY,
    lcMagnitude: () => lcMagnitude,
    readabilityTier: () => readabilityTier,
    testCases: () => testCases2
  });
  var MAIN_TRC = 2.4;
  var SR_CO = 0.2126729;
  var SG_CO = 0.7151522;
  var SB_CO = 0.072175;
  var NORM_BG = 0.56;
  var NORM_TXT = 0.57;
  var REV_TXT = 0.62;
  var REV_BG = 0.65;
  var BLK_THRS = 0.022;
  var BLK_CLMP = 1.414;
  var SCALE_BOW = 1.14;
  var SCALE_WOB = 1.14;
  var LO_BOW_OFFSET = 0.027;
  var LO_WOB_OFFSET = 0.027;
  var DELTA_Y_MIN = 5e-4;
  var LO_CLIP = 0.1;
  function apcaY(rgb) {
    const r = Math.pow(rgb[0], MAIN_TRC);
    const g = Math.pow(rgb[1], MAIN_TRC);
    const b = Math.pow(rgb[2], MAIN_TRC);
    let y = SR_CO * r + SG_CO * g + SB_CO * b;
    if (y < BLK_THRS) {
      y = y + Math.pow(BLK_THRS - y, BLK_CLMP);
    }
    return y;
  }
  function apcaContrast(text, bg) {
    const txtY = apcaY(text);
    const bgY = apcaY(bg);
    if (Math.abs(bgY - txtY) < DELTA_Y_MIN)
      return 0;
    let SAPC = 0;
    if (bgY > txtY) {
      const C5 = SCALE_BOW * (Math.pow(bgY, NORM_BG) - Math.pow(txtY, NORM_TXT));
      if (C5 < LO_CLIP) {
        SAPC = 0;
      } else if (C5 < LO_BOW_OFFSET) {
        SAPC = C5 - C5 * 32.8 * (LO_BOW_OFFSET - C5) / LO_BOW_OFFSET;
      } else {
        SAPC = C5 - LO_BOW_OFFSET;
      }
      return SAPC * 100;
    } else {
      const C5 = SCALE_WOB * (Math.pow(bgY, REV_BG) - Math.pow(txtY, REV_TXT));
      if (C5 > -LO_CLIP) {
        SAPC = 0;
      } else if (C5 > -LO_WOB_OFFSET) {
        SAPC = C5 - C5 * 32.8 * (-LO_WOB_OFFSET - C5) / -LO_WOB_OFFSET;
      } else {
        SAPC = C5 + LO_WOB_OFFSET;
      }
      return SAPC * 100;
    }
  }
  var lcMagnitude = (lc) => Math.abs(lc);
  function readabilityTier(lc) {
    const m = Math.abs(lc);
    if (m >= 90)
      return "optimal";
    if (m >= 75)
      return "fluent-body";
    if (m >= 60)
      return "body-minimum";
    if (m >= 45)
      return "heading-or-large-body";
    if (m >= 30)
      return "large-heading";
    if (m >= 15)
      return "non-text-only";
    return "insufficient";
  }
  var testCases2 = [
    {
      name: "apca identity (same color = 0)",
      fn: () => apcaContrast(encodedSRGB(0.5, 0.5, 0.5), encodedSRGB(0.5, 0.5, 0.5)),
      expected: 0,
      tolerance: 1e-9,
      source: "Trivial identity"
    },
    {
      name: "apca pure black-on-white returns large positive",
      fn: () => apcaContrast(encodedSRGB(0, 0, 0), encodedSRGB(1, 1, 1)),
      expected: 106,
      tolerance: 0.5,
      source: "APCA-W3 reference; pure black on white ~= 106"
    },
    {
      name: "apca pure white-on-black returns large negative",
      fn: () => apcaContrast(encodedSRGB(1, 1, 1), encodedSRGB(0, 0, 0)),
      expected: -107.88,
      tolerance: 0.5,
      source: "APCA-W3 reference; pure white on black ~= -107.88"
    }
  ];

  // lib/dist/metrics/deltaE.js
  var deltaE_exports = {};
  __export(deltaE_exports, {
    deltaE2000: () => deltaE2000,
    deltaE76: () => deltaE76,
    deltaE94: () => deltaE94,
    deltaEOK: () => deltaEOK,
    hyAB: () => hyAB,
    testCases: () => testCases3
  });
  function deltaE76(a, b) {
    const dL = a[0] - b[0];
    const dA = a[1] - b[1];
    const dB = a[2] - b[2];
    return Math.sqrt(dL * dL + dA * dA + dB * dB);
  }
  function deltaE94(a, b, textiles = false) {
    const [L1, a1, b1] = a;
    const [L2, a2, b2] = b;
    const C14 = Math.hypot(a1, b1);
    const C24 = Math.hypot(a2, b2);
    const dC = C14 - C24;
    const dL = L1 - L2;
    const dA = a1 - a2;
    const dB = b1 - b2;
    const dH2 = Math.max(0, dA * dA + dB * dB - dC * dC);
    const kL = textiles ? 2 : 1;
    const K1 = textiles ? 0.048 : 0.045;
    const K2 = textiles ? 0.014 : 0.015;
    const sL = 1;
    const sC = 1 + K1 * C14;
    const sH = 1 + K2 * C14;
    const tL = dL / (kL * sL);
    const tC = dC / sC;
    return Math.sqrt(tL * tL + tC * tC + dH2 / (sH * sH));
  }
  function deltaE2000(a, b, kL = 1, kC = 1, kH = 1) {
    const [L1, a1, b1] = a;
    const [L2, a2, b2] = b;
    const C14 = Math.hypot(a1, b1);
    const C24 = Math.hypot(a2, b2);
    const Cbar = (C14 + C24) / 2;
    const Cbar7 = Math.pow(Cbar, 7);
    const G2 = 0.5 * (1 - Math.sqrt(Cbar7 / (Cbar7 + Math.pow(25, 7))));
    const a1p = (1 + G2) * a1;
    const a2p = (1 + G2) * a2;
    const C1p = Math.hypot(a1p, b1);
    const C2p = Math.hypot(a2p, b2);
    const h1p = (() => {
      if (b1 === 0 && a1p === 0)
        return 0;
      const h = Math.atan2(b1, a1p) * 180 / Math.PI;
      return h < 0 ? h + 360 : h;
    })();
    const h2p = (() => {
      if (b2 === 0 && a2p === 0)
        return 0;
      const h = Math.atan2(b2, a2p) * 180 / Math.PI;
      return h < 0 ? h + 360 : h;
    })();
    const dLp = L2 - L1;
    const dCp = C2p - C1p;
    let dhp = 0;
    if (C1p === 0 || C2p === 0) {
      dhp = 0;
    } else {
      const diff = h2p - h1p;
      if (Math.abs(diff) <= 180)
        dhp = diff;
      else if (diff > 180)
        dhp = diff - 360;
      else
        dhp = diff + 360;
    }
    const dHp = 2 * Math.sqrt(C1p * C2p) * Math.sin(dhp / 2 * Math.PI / 180);
    const Lbar = (L1 + L2) / 2;
    const Cbarp = (C1p + C2p) / 2;
    let hbarp;
    if (C1p === 0 || C2p === 0) {
      hbarp = h1p + h2p;
    } else if (Math.abs(h1p - h2p) <= 180) {
      hbarp = (h1p + h2p) / 2;
    } else if (h1p + h2p < 360) {
      hbarp = (h1p + h2p + 360) / 2;
    } else {
      hbarp = (h1p + h2p - 360) / 2;
    }
    const T = 1 - 0.17 * Math.cos((hbarp - 30) * Math.PI / 180) + 0.24 * Math.cos(2 * hbarp * Math.PI / 180) + 0.32 * Math.cos((3 * hbarp + 6) * Math.PI / 180) - 0.2 * Math.cos((4 * hbarp - 63) * Math.PI / 180);
    const dTheta = 30 * Math.exp(-Math.pow((hbarp - 275) / 25, 2));
    const Rc = 2 * Math.sqrt(Math.pow(Cbarp, 7) / (Math.pow(Cbarp, 7) + Math.pow(25, 7)));
    const Sl = 1 + 0.015 * Math.pow(Lbar - 50, 2) / Math.sqrt(20 + Math.pow(Lbar - 50, 2));
    const Sc = 1 + 0.045 * Cbarp;
    const Sh = 1 + 0.015 * Cbarp * T;
    const Rt = -Math.sin(2 * dTheta * Math.PI / 180) * Rc;
    const tL = dLp / (kL * Sl);
    const tC = dCp / (kC * Sc);
    const tH = dHp / (kH * Sh);
    return Math.sqrt(tL * tL + tC * tC + tH * tH + Rt * tC * tH);
  }
  function deltaEOK(a, b) {
    const dL = a[0] - b[0];
    const dA = a[1] - b[1];
    const dB = a[2] - b[2];
    return Math.sqrt(dL * dL + dA * dA + dB * dB);
  }
  function hyAB(a, b) {
    const dL = a[0] - b[0];
    const dA = Math.abs(a[1] - b[1]);
    const dB = Math.abs(a[2] - b[2]);
    return Math.sqrt(dL * dL) + dA + dB;
  }
  var testCases3 = [
    // Identity: same color → 0
    {
      name: "deltaE76 identity",
      fn: () => deltaE76(cielab_D65(50, 10, -20), cielab_D65(50, 10, -20)),
      expected: 0,
      tolerance: 1e-12,
      source: "Trivial identity"
    },
    {
      name: "deltaE2000 identity",
      fn: () => deltaE2000(cielab_D65(50, 10, -20), cielab_D65(50, 10, -20)),
      expected: 0,
      tolerance: 1e-12,
      source: "Trivial identity"
    },
    {
      name: "deltaEOK identity",
      fn: () => deltaEOK(oklab(0.5, 0.1, -0.05), oklab(0.5, 0.1, -0.05)),
      expected: 0,
      tolerance: 1e-12,
      source: "Trivial identity"
    },
    // Sharma et al. (2005), Table 1 — selected CIEDE2000 test pairs:
    {
      name: "deltaE2000 Sharma pair 1 (50,2.6772,-79.7751 vs 50,0,-82.7485)",
      fn: () => deltaE2000(cielab_D65(50, 2.6772, -79.7751), cielab_D65(50, 0, -82.7485)),
      expected: 2.0425,
      tolerance: 5e-4,
      source: "Sharma/Wu/Dalal 2005 Table 1 pair 1"
    },
    {
      name: "deltaE2000 Sharma pair 2 (50,3.1571,-77.2803 vs 50,0,-82.7485)",
      fn: () => deltaE2000(cielab_D65(50, 3.1571, -77.2803), cielab_D65(50, 0, -82.7485)),
      expected: 2.8615,
      tolerance: 5e-4,
      source: "Sharma/Wu/Dalal 2005 Table 1 pair 2"
    },
    // deltaE76: pure perpendicular axis distance
    {
      name: "deltaE76 axis distance (a)",
      fn: () => deltaE76(cielab_D65(50, 0, 0), cielab_D65(50, 50, 0)),
      expected: 50,
      tolerance: 1e-12,
      source: "Trivial axis-aligned distance"
    },
    // HyAB: city-block in (a, b)
    {
      name: "hyAB city-block (a, b)",
      fn: () => hyAB(cielab_D65(50, 0, 0), cielab_D65(50, 3, 4)),
      expected: 7,
      tolerance: 1e-12,
      source: "Pure (a, b) city-block distance: 3 + 4 = 7"
    }
  ];

  // lib/dist/adaptation/bradford.js
  var bradford_exports = {};
  __export(bradford_exports, {
    A: () => A2,
    D50: () => D50,
    D65: () => D65,
    F2: () => F2,
    M_BRADFORD: () => M_BRADFORD,
    M_BRADFORD_INV: () => M_BRADFORD_INV,
    M_D50_TO_D65: () => M_D50_TO_D65,
    M_D65_TO_D50: () => M_D65_TO_D50,
    adapt: () => adapt,
    bradfordMatrix: () => bradfordMatrix,
    d50ToD65: () => d50ToD65,
    d65ToD50: () => d65ToD50,
    testCases: () => testCases4
  });
  var M_BRADFORD = [
    [0.8951, 0.2664, -0.1614],
    [-0.7502, 1.7135, 0.0367],
    [0.0389, -0.0685, 1.0296]
  ];
  var M_BRADFORD_INV = [
    [0.9869929, -0.1470543, 0.1599627],
    [0.4323053, 0.5183603, 0.0492912],
    [-85287e-7, 0.0400428, 0.9684867]
  ];
  var D65 = [0.9504559270516716, 1, 1.0890577507598784];
  var D50 = [0.9642956764295677, 1, 0.8251046025104602];
  var A2 = [1.0985, 1, 0.35585];
  var F2 = [0.99186, 1, 0.67393];
  function bradfordMatrix(srcWhite, dstWhite) {
    const rgbSrc = mulMat3Vec3(M_BRADFORD, srcWhite);
    const rgbDst = mulMat3Vec3(M_BRADFORD, dstWhite);
    const D2 = [
      [rgbDst[0] / rgbSrc[0], 0, 0],
      [0, rgbDst[1] / rgbSrc[1], 0],
      [0, 0, rgbDst[2] / rgbSrc[2]]
    ];
    return mulMat3Mat3(M_BRADFORD_INV, mulMat3Mat3(D2, M_BRADFORD));
  }
  function adapt(srcXYZ, srcWhite, dstWhite) {
    const M3 = bradfordMatrix(srcWhite, dstWhite);
    return mulMat3Vec3(M3, srcXYZ);
  }
  var M_D50_TO_D65 = bradfordMatrix(D50, D65);
  var M_D65_TO_D50 = bradfordMatrix(D65, D50);
  function d50ToD65(xyzD50) {
    const [X, Y, Z] = mulMat3Vec3(M_D50_TO_D65, xyzD50);
    return xyz(X, Y, Z);
  }
  function d65ToD50(xyzD65) {
    return mulMat3Vec3(M_D65_TO_D50, xyzD65);
  }
  var testCases4 = [
    {
      name: "bradford D65 \u2192 D65 = identity Y",
      fn: () => {
        const adapted = adapt(D65, D65, D65);
        return Math.abs(adapted[1] - 1);
      },
      expected: 0,
      tolerance: 1e-6,
      source: "Self-adaptation should be identity (within published-matrix precision)"
    },
    {
      name: "bradford D50 \u2194 D65 round-trip Y",
      fn: () => {
        const round = adapt(adapt(D65, D65, D50), D50, D65);
        return Math.abs(round[1] - 1);
      },
      expected: 0,
      tolerance: 1e-6,
      source: "Round-trip should restore Y=1 within published-matrix precision"
    },
    {
      name: "bradford D65 \u2192 D50 maps D65 white to D50 white",
      fn: () => {
        const adapted = adapt(D65, D65, D50);
        return Math.hypot(adapted[0] - D50[0], adapted[1] - D50[1], adapted[2] - D50[2]);
      },
      expected: 0,
      tolerance: 1e-6,
      source: "White points must map to white points"
    }
  ];

  // lib/dist/cvd/machado-2009.js
  var machado_2009_exports = {};
  __export(machado_2009_exports, {
    M_DEUTERANOPIA: () => M_DEUTERANOPIA,
    M_PROTANOPIA: () => M_PROTANOPIA,
    M_TRITANOPIA: () => M_TRITANOPIA,
    simulate: () => simulate,
    simulateDeuteranopia: () => simulateDeuteranopia,
    simulateProtanopia: () => simulateProtanopia,
    simulateTritanopia: () => simulateTritanopia,
    simulationMatrix: () => simulationMatrix,
    testCases: () => testCases5
  });
  var M_PROTANOPIA = [
    [0.152286, 1.052583, -0.204868],
    [0.114503, 0.786281, 0.099216],
    [-3882e-6, -0.048116, 1.051998]
  ];
  var M_DEUTERANOPIA = [
    [0.367322, 0.860646, -0.227968],
    [0.280085, 0.672501, 0.047413],
    [-0.01182, 0.04294, 0.968881]
  ];
  var M_TRITANOPIA = [
    [1.255528, -0.076749, -0.178779],
    [-0.078411, 0.930809, 0.147602],
    [4733e-6, 0.691367, 0.3039]
  ];
  var IDENTITY = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
  ];
  var TYPE_MATRIX = {
    protanopia: M_PROTANOPIA,
    deuteranopia: M_DEUTERANOPIA,
    tritanopia: M_TRITANOPIA
  };
  function lerpMatrix(a, b, t) {
    const r = (i, j) => a[i][j] + (b[i][j] - a[i][j]) * t;
    return [
      [r(0, 0), r(0, 1), r(0, 2)],
      [r(1, 0), r(1, 1), r(1, 2)],
      [r(2, 0), r(2, 1), r(2, 2)]
    ];
  }
  function simulationMatrix(type, severity = 1) {
    const s = Math.max(0, Math.min(1, severity));
    if (s === 0)
      return IDENTITY;
    if (s === 1)
      return TYPE_MATRIX[type];
    return lerpMatrix(IDENTITY, TYPE_MATRIX[type], s);
  }
  function simulate(rgb, type, severity = 1) {
    const M3 = simulationMatrix(type, severity);
    const [r, g, b] = mulMat3Vec3(M3, rgb);
    return linearSRGB(r, g, b);
  }
  var simulateProtanopia = (rgb, severity = 1) => simulate(rgb, "protanopia", severity);
  var simulateDeuteranopia = (rgb, severity = 1) => simulate(rgb, "deuteranopia", severity);
  var simulateTritanopia = (rgb, severity = 1) => simulate(rgb, "tritanopia", severity);
  var testCases5 = [
    {
      name: "severity=0 returns identity (protanopia)",
      fn: () => {
        const input = linearSRGB(0.5, 0.3, 0.7);
        const out = simulate(input, "protanopia", 0);
        return Math.hypot(out[0] - 0.5, out[1] - 0.3, out[2] - 0.7);
      },
      expected: 0,
      tolerance: 1e-12,
      source: "Severity 0 = no deficiency = identity transform"
    },
    {
      name: "severity=0 returns identity (deuteranopia)",
      fn: () => {
        const input = linearSRGB(0.8, 0.2, 0.4);
        const out = simulate(input, "deuteranopia", 0);
        return Math.hypot(out[0] - 0.8, out[1] - 0.2, out[2] - 0.4);
      },
      expected: 0,
      tolerance: 1e-12,
      source: "Severity 0 = no deficiency = identity transform"
    },
    {
      name: "black is unchanged (protanopia)",
      fn: () => {
        const out = simulate(linearSRGB(0, 0, 0), "protanopia", 1);
        return Math.hypot(...out);
      },
      expected: 0,
      tolerance: 1e-12,
      source: "Black has no chromatic component; CVD simulation preserves it"
    },
    {
      name: "white is approximately unchanged (deuteranopia)",
      fn: () => {
        const out = simulate(linearSRGB(1, 1, 1), "deuteranopia", 1);
        return Math.hypot(out[0] - 1, out[1] - 1, out[2] - 1);
      },
      expected: 0,
      tolerance: 1e-3,
      source: "CVD matrix rows sum to ~1 (preserves white)"
    },
    {
      name: "severity=1 protanopia desaturates pure red",
      fn: () => {
        const input = linearSRGB(1, 0, 0);
        const out = simulate(input, "protanopia", 1);
        return out[0];
      },
      expected: 0.152286,
      tolerance: 1e-5,
      source: "Machado 2009 \u2014 pure red under protanopia maps to ~0.152"
    },
    {
      name: "severity=0.5 is midpoint between identity and full",
      fn: () => {
        const input = linearSRGB(1, 0, 0);
        const full = simulate(input, "protanopia", 1);
        const half = simulate(input, "protanopia", 0.5);
        const expectedR = 0.5 * (1 + full[0]);
        return Math.abs(half[0] - expectedR);
      },
      expected: 0,
      tolerance: 1e-9,
      source: "Linear interpolation: severity 0.5 = mean of identity and full"
    }
  ];

  // lib/dist/interpolation/linear.js
  var linear_exports = {};
  __export(linear_exports, {
    lerpCielab: () => lerpCielab,
    lerpCielch: () => lerpCielch,
    lerpHue: () => lerpHue,
    lerpOklab: () => lerpOklab,
    lerpOklch: () => lerpOklch,
    lerpTuple: () => lerpTuple,
    mixVia: () => mixVia,
    rampOklab: () => rampOklab,
    rampOklch: () => rampOklch,
    stops: () => stops,
    testCases: () => testCases6
  });
  function lerpHue(h1, h2, t, path = "shorter") {
    h1 = wrapHueDeg(h1);
    h2 = wrapHueDeg(h2);
    const diff = h2 - h1;
    let effDiff;
    switch (path) {
      case "shorter":
        if (Math.abs(diff) <= 180)
          effDiff = diff;
        else if (diff > 180)
          effDiff = diff - 360;
        else
          effDiff = diff + 360;
        break;
      case "longer":
        if (Math.abs(diff) >= 180)
          effDiff = diff;
        else if (diff > 0)
          effDiff = diff - 360;
        else
          effDiff = diff + 360;
        break;
      case "increasing":
        effDiff = diff < 0 ? diff + 360 : diff;
        break;
      case "decreasing":
        effDiff = diff > 0 ? diff - 360 : diff;
        break;
    }
    return wrapHueDeg(h1 + t * effDiff);
  }
  function lerpTuple(a, b, t) {
    return [
      a[0] + (b[0] - a[0]) * t,
      a[1] + (b[1] - a[1]) * t,
      a[2] + (b[2] - a[2]) * t
    ];
  }
  function lerpOklab(a, b, t) {
    return lerpTuple(a, b, t);
  }
  function lerpCielab(a, b, t) {
    return lerpTuple(a, b, t);
  }
  function lerpOklch(a, b, t, huePath = "shorter") {
    return [
      a[0] + (b[0] - a[0]) * t,
      a[1] + (b[1] - a[1]) * t,
      lerpHue(a[2], b[2], t, huePath)
    ];
  }
  function lerpCielch(a, b, t, huePath = "shorter") {
    return [
      a[0] + (b[0] - a[0]) * t,
      a[1] + (b[1] - a[1]) * t,
      lerpHue(a[2], b[2], t, huePath)
    ];
  }
  function mixVia(a, b, t, sourceSpace, viaSpace) {
    const aVia = viaSpace.fromXYZ(sourceSpace.toXYZ(a));
    const bVia = viaSpace.fromXYZ(sourceSpace.toXYZ(b));
    const mixed = lerpTuple(aVia, bVia, t);
    return sourceSpace.fromXYZ(viaSpace.toXYZ(mixed));
  }
  function stops(n) {
    if (n <= 1)
      return [0];
    const out = [];
    for (let i = 0; i < n; i++) {
      out.push(i / (n - 1));
    }
    return out;
  }
  function rampOklab(a, b, n) {
    return stops(n).map((t) => lerpOklab(a, b, t));
  }
  function rampOklch(a, b, n, huePath = "shorter") {
    return stops(n).map((t) => lerpOklch(a, b, t, huePath));
  }
  var testCases6 = [
    {
      name: "lerpHue shorter 350\xB0 \u2192 10\xB0 at t=0.5 yields 0\xB0 (wraps)",
      fn: () => lerpHue(350, 10, 0.5, "shorter"),
      expected: 0,
      tolerance: 1e-9,
      source: "CSS Color 4 \u2014 shorter arc across 0\xB0 boundary is 20\xB0 total"
    },
    {
      name: "lerpHue longer 350\xB0 \u2192 10\xB0 at t=0.5 yields 180\xB0",
      fn: () => lerpHue(350, 10, 0.5, "longer"),
      expected: 180,
      tolerance: 1e-9,
      source: "CSS Color 4 \u2014 longer arc across 0\xB0 boundary is 340\xB0 total \u2192 midpoint 180\xB0"
    },
    {
      name: "lerpHue increasing 350\xB0 \u2192 10\xB0 at t=0.5 yields 0\xB0",
      fn: () => lerpHue(350, 10, 0.5, "increasing"),
      expected: 0,
      tolerance: 1e-9,
      source: "CSS Color 4 \u2014 increasing 350\xB0 \u2192 370\xB0 \u2192 10\xB0"
    },
    {
      name: "lerpHue decreasing 10\xB0 \u2192 350\xB0 at t=0.5 yields 0\xB0",
      fn: () => lerpHue(10, 350, 0.5, "decreasing"),
      expected: 0,
      tolerance: 1e-9,
      source: "CSS Color 4 \u2014 decreasing 10\xB0 \u2192 -10\xB0 \u2192 350\xB0 via 0\xB0"
    },
    {
      name: "lerpHue same hue returns same hue",
      fn: () => lerpHue(120, 120, 0.5, "shorter"),
      expected: 120,
      tolerance: 1e-9,
      source: "Identity case"
    },
    {
      name: "lerpTuple at t=0 returns a",
      fn: () => lerpTuple([1, 2, 3], [4, 5, 6], 0)[1],
      expected: 2,
      tolerance: 1e-12,
      source: "Endpoint at t=0"
    },
    {
      name: "lerpTuple at t=1 returns b",
      fn: () => lerpTuple([1, 2, 3], [4, 5, 6], 1)[1],
      expected: 5,
      tolerance: 1e-12,
      source: "Endpoint at t=1"
    },
    {
      name: "lerpTuple midpoint averages",
      fn: () => lerpTuple([0, 0, 0], [10, 20, 30], 0.5)[2],
      expected: 15,
      tolerance: 1e-12,
      source: "Midpoint of 0 and 30 is 15"
    },
    {
      name: "stops(5) is uniformly spaced",
      fn: () => stops(5)[2],
      expected: 0.5,
      tolerance: 1e-12,
      source: "stops(5) = [0, 0.25, 0.5, 0.75, 1.0]"
    }
  ];

  // lib/dist/interpolation/cubehelix.js
  var cubehelix_exports = {};
  __export(cubehelix_exports, {
    DEFAULT_OPTIONS: () => DEFAULT_OPTIONS,
    cubehelix: () => cubehelix,
    cubehelixPalette: () => cubehelixPalette,
    testCases: () => testCases7
  });
  var TWO_PI = Math.PI * 2;
  var DEG_TO_RAD4 = Math.PI / 180;
  var DEFAULT_OPTIONS = {
    start: 0,
    rotations: -1.5,
    hue: 1,
    gamma: 1
  };
  function cubehelix(t, opts = {}) {
    const { start, rotations, hue, gamma } = { ...DEFAULT_OPTIONS, ...opts };
    const l = Math.pow(t, gamma);
    const angle = TWO_PI * (start / 360 + 1 + rotations * t);
    const amp = hue * l * (1 - l) / 2;
    const cos = Math.cos(angle);
    const sin = Math.sin(angle);
    const r = l + amp * (-0.14861 * cos + 1.78277 * sin);
    const g = l + amp * (-0.29227 * cos - 0.90649 * sin);
    const b = l + amp * (1.97294 * cos);
    return linearSRGB(r, g, b);
  }
  function cubehelixPalette(n, opts = {}) {
    if (n <= 1)
      return [cubehelix(0, opts)];
    const out = [];
    for (let i = 0; i < n; i++) {
      out.push(cubehelix(i / (n - 1), opts));
    }
    return out;
  }
  var testCases7 = [
    {
      name: "cubehelix at t=0 is black",
      fn: () => Math.hypot(...cubehelix(0)),
      expected: 0,
      tolerance: 1e-12,
      source: "Green 2011 \u2014 t=0 is the black anchor (l=0 \u2192 R=G=B=0)"
    },
    {
      name: "cubehelix at t=1 is white",
      fn: () => {
        const c = cubehelix(1);
        return Math.hypot(c[0] - 1, c[1] - 1, c[2] - 1);
      },
      expected: 0,
      tolerance: 1e-12,
      source: "Green 2011 \u2014 t=1 is the white anchor (l=1, amp=0 \u2192 R=G=B=1)"
    },
    {
      name: "cubehelix at t=0.5 has reasonable mid-tone luminance",
      fn: () => {
        const c = cubehelix(0.5);
        const Y = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
        return Y;
      },
      expected: 0.5,
      tolerance: 0.1,
      source: "Cubehelix is designed for monotonic Y; mid-t should give Y ~0.5"
    },
    {
      name: "cubehelix palette of 5 starts at black",
      fn: () => Math.hypot(...cubehelixPalette(5)[0]),
      expected: 0,
      tolerance: 1e-12,
      source: "Palette inclusive of endpoints"
    },
    {
      name: "cubehelix palette of 5 ends at white",
      fn: () => {
        const last = cubehelixPalette(5)[4];
        return Math.hypot(last[0] - 1, last[1] - 1, last[2] - 1);
      },
      expected: 0,
      tolerance: 1e-12,
      source: "Palette inclusive of endpoints"
    }
  ];

  // lib/dist/interpolation/lightness-curves.js
  var lightness_curves_exports = {};
  __export(lightness_curves_exports, {
    RADIX_THEMES_3_L_STOPS_LIGHT: () => RADIX_THEMES_3_L_STOPS_LIGHT,
    TAILWIND_V4_L_STOPS: () => TAILWIND_V4_L_STOPS,
    gammaRamp: () => gammaRamp,
    linearRamp: () => linearRamp,
    perceptualRamp: () => perceptualRamp,
    radixLightLAtStep: () => radixLightLAtStep,
    smoothstepRamp: () => smoothstepRamp,
    tailwindV4LAtStep: () => tailwindV4LAtStep,
    testCases: () => testCases8
  });
  function linearRamp(t, lMin = 0, lMax = 1) {
    return lMin + t * (lMax - lMin);
  }
  function gammaRamp(t, gamma, lMin = 0, lMax = 1) {
    return lMin + Math.pow(t, gamma) * (lMax - lMin);
  }
  function perceptualRamp(t, lMin = 0, lMax = 1) {
    return lMin + t * (lMax - lMin);
  }
  function smoothstepRamp(t, lMin = 0, lMax = 1) {
    const s = t * t * (3 - 2 * t);
    return lMin + s * (lMax - lMin);
  }
  var TAILWIND_V4_L_STOPS = [
    0.985,
    // 50
    0.967,
    // 100
    0.922,
    // 200
    0.87,
    // 300
    0.708,
    // 400
    0.554,
    // 500
    0.446,
    // 600
    0.371,
    // 700
    0.269,
    // 800
    0.205,
    // 900
    0.13
    // 950
  ];
  function tailwindV4LAtStep(step) {
    const stepMap = {
      50: 0,
      100: 1,
      200: 2,
      300: 3,
      400: 4,
      500: 5,
      600: 6,
      700: 7,
      800: 8,
      900: 9,
      950: 10
    };
    const idx = stepMap[step];
    if (idx === void 0) {
      throw new Error(`Tailwind v4 step must be one of 50, 100, 200, ..., 950 (got ${step})`);
    }
    return TAILWIND_V4_L_STOPS[idx];
  }
  var RADIX_THEMES_3_L_STOPS_LIGHT = [
    0.995,
    0.988,
    0.965,
    0.93,
    0.879,
    0.821,
    0.756,
    0.673,
    0.564,
    0.481,
    0.396,
    0.18
  ];
  function radixLightLAtStep(step) {
    if (step < 1 || step > 12 || !Number.isInteger(step)) {
      throw new Error(`Radix step must be integer 1-12 (got ${step})`);
    }
    return RADIX_THEMES_3_L_STOPS_LIGHT[step - 1];
  }
  var testCases8 = [
    {
      name: "linearRamp(0.5) = 0.5 default",
      fn: () => linearRamp(0.5),
      expected: 0.5,
      tolerance: 1e-12,
      source: "Trivial midpoint"
    },
    {
      name: "linearRamp(0.5, 0.2, 0.8) = 0.5",
      fn: () => linearRamp(0.5, 0.2, 0.8),
      expected: 0.5,
      tolerance: 1e-12,
      source: "Midpoint of [0.2, 0.8] is 0.5"
    },
    {
      name: "gammaRamp(0.5, 2) = 0.25 (slow start)",
      fn: () => gammaRamp(0.5, 2),
      expected: 0.25,
      tolerance: 1e-12,
      source: "0.5^2 = 0.25"
    },
    {
      name: "gammaRamp(0.5, 0.5) = sqrt(0.5)",
      fn: () => gammaRamp(0.5, 0.5),
      expected: Math.sqrt(0.5),
      tolerance: 1e-12,
      source: "0.5^0.5 = sqrt(0.5) \u2248 0.707"
    },
    {
      name: "smoothstepRamp(0.5) = 0.5",
      fn: () => smoothstepRamp(0.5),
      expected: 0.5,
      tolerance: 1e-12,
      source: "0.5\xB2(3 - 2\xB70.5) = 0.25 \xB7 2 = 0.5; smoothstep is symmetric at midpoint"
    },
    {
      name: "smoothstepRamp(0) = 0",
      fn: () => smoothstepRamp(0),
      expected: 0,
      tolerance: 1e-12,
      source: "Endpoint anchor"
    },
    {
      name: "tailwindV4LAtStep(500) = 0.554",
      fn: () => tailwindV4LAtStep(500),
      expected: 0.554,
      tolerance: 1e-9,
      source: "Tailwind v4 step 500 (mid)"
    },
    {
      name: "tailwindV4LAtStep(950) is darkest",
      fn: () => tailwindV4LAtStep(950),
      expected: 0.13,
      tolerance: 1e-9,
      source: "Tailwind v4 step 950"
    },
    {
      name: "radixLightLAtStep(1) is lightest",
      fn: () => radixLightLAtStep(1),
      expected: 0.995,
      tolerance: 1e-9,
      source: "Radix step 1 (app background, near-white)"
    },
    {
      name: "radixLightLAtStep(12) is darkest",
      fn: () => radixLightLAtStep(12),
      expected: 0.18,
      tolerance: 1e-9,
      source: "Radix step 12 (high-contrast text, dark)"
    }
  ];

  // lib/dist/interpolation/spline.js
  var spline_exports = {};
  __export(spline_exports, {
    catmullRomCurve: () => catmullRomCurve,
    catmullRomSamples: () => catmullRomSamples,
    catmullRomScalar: () => catmullRomScalar,
    catmullRomTuple: () => catmullRomTuple,
    testCases: () => testCases9
  });
  function catmullRomScalar(P0, P1, P2, P3, t) {
    const t2 = t * t;
    const t3 = t2 * t;
    return 0.5 * (2 * P1 + (-P0 + P2) * t + (2 * P0 - 5 * P1 + 4 * P2 - P3) * t2 + (-P0 + 3 * P1 - 3 * P2 + P3) * t3);
  }
  function catmullRomTuple(P0, P1, P2, P3, t) {
    return [
      catmullRomScalar(P0[0], P1[0], P2[0], P3[0], t),
      catmullRomScalar(P0[1], P1[1], P2[1], P3[1], t),
      catmullRomScalar(P0[2], P1[2], P2[2], P3[2], t)
    ];
  }
  function catmullRomCurve(controls, t) {
    if (controls.length < 2) {
      throw new Error("catmullRomCurve requires at least 2 control points");
    }
    if (controls.length === 2) {
      return [
        controls[0][0] + (controls[1][0] - controls[0][0]) * t,
        controls[0][1] + (controls[1][1] - controls[0][1]) * t,
        controls[0][2] + (controls[1][2] - controls[0][2]) * t
      ];
    }
    const n = controls.length - 1;
    const u = Math.max(0, Math.min(1, t)) * n;
    const segment = Math.min(Math.floor(u), n - 1);
    const localT = u - segment;
    const P0 = controls[Math.max(0, segment - 1)];
    const P1 = controls[segment];
    const P2 = controls[segment + 1];
    const P3 = controls[Math.min(n, segment + 2)];
    return catmullRomTuple(P0, P1, P2, P3, localT);
  }
  function catmullRomSamples(controls, n) {
    if (n < 2)
      return [catmullRomCurve(controls, 0)];
    const out = [];
    for (let i = 0; i < n; i++) {
      out.push(catmullRomCurve(controls, i / (n - 1)));
    }
    return out;
  }
  var testCases9 = [
    {
      name: "Catmull-Rom passes through P1 at t=0",
      fn: () => Math.abs(catmullRomScalar(0, 1, 2, 3, 0) - 1),
      expected: 0,
      tolerance: 1e-12,
      source: "Curve interpolates P1 exactly at t=0"
    },
    {
      name: "Catmull-Rom passes through P2 at t=1",
      fn: () => Math.abs(catmullRomScalar(0, 1, 2, 3, 1) - 2),
      expected: 0,
      tolerance: 1e-12,
      source: "Curve interpolates P2 exactly at t=1"
    },
    {
      name: "Catmull-Rom on linear data is linear",
      fn: () => {
        return Math.abs(catmullRomScalar(0, 1, 2, 3, 0.5) - 1.5);
      },
      expected: 0,
      tolerance: 1e-12,
      source: "For linearly-spaced controls, Catmull-Rom is linear"
    },
    {
      name: "catmullRomCurve through 3 points hits first control",
      fn: () => {
        const pts = [[0, 0, 0], [1, 2, 3], [2, 4, 6]];
        const result = catmullRomCurve(pts, 0);
        return Math.hypot(result[0], result[1], result[2]);
      },
      expected: 0,
      tolerance: 1e-12,
      source: "Endpoint anchoring"
    },
    {
      name: "catmullRomCurve through 3 points hits last control",
      fn: () => {
        const pts = [[0, 0, 0], [1, 2, 3], [2, 4, 6]];
        const result = catmullRomCurve(pts, 1);
        return Math.hypot(result[0] - 2, result[1] - 4, result[2] - 6);
      },
      expected: 0,
      tolerance: 1e-12,
      source: "Endpoint anchoring"
    }
  ];

  // lib/dist/gamut/cusp.js
  var cusp_exports = {};
  __export(cusp_exports, {
    findCuspSRGB: () => findCuspSRGB,
    findCuspSRGBFromHueDeg: () => findCuspSRGBFromHueDeg,
    maxSaturationSRGB: () => maxSaturationSRGB,
    testCases: () => testCases10
  });
  var DEG_TO_RAD5 = Math.PI / 180;
  function maxSaturationSRGB(a, b) {
    let k0, k1, k2, k3, k4;
    let wl, wm, ws;
    if (-1.88170328 * a - 0.80936493 * b > 1) {
      k0 = 1.19086277;
      k1 = 1.76576728;
      k2 = 0.59662641;
      k3 = 0.75515197;
      k4 = 0.56771245;
      wl = 4.0767416621;
      wm = -3.3077115913;
      ws = 0.2309699292;
    } else if (1.81444104 * a - 1.19445276 * b > 1) {
      k0 = 0.73956515;
      k1 = -0.45954404;
      k2 = 0.08285427;
      k3 = 0.1254107;
      k4 = 0.14503204;
      wl = -1.2684380046;
      wm = 2.6097574011;
      ws = -0.3413193965;
    } else {
      k0 = 1.35733652;
      k1 = -915799e-8;
      k2 = -1.1513021;
      k3 = -0.50559606;
      k4 = 692167e-8;
      wl = -0.0041960863;
      wm = -0.7034186147;
      ws = 1.707614701;
    }
    let S = k0 + k1 * a + k2 * b + k3 * a * a + k4 * a * b;
    const k_l = 0.3963377774 * a + 0.2158037573 * b;
    const k_m = -0.1055613458 * a + -0.0638541728 * b;
    const k_s = -0.0894841775 * a + -1.291485548 * b;
    const l_ = 1 + S * k_l;
    const m_ = 1 + S * k_m;
    const s_ = 1 + S * k_s;
    const l = l_ * l_ * l_;
    const m = m_ * m_ * m_;
    const s = s_ * s_ * s_;
    const l_dS = 3 * k_l * l_ * l_;
    const m_dS = 3 * k_m * m_ * m_;
    const s_dS = 3 * k_s * s_ * s_;
    const l_dS2 = 6 * k_l * k_l * l_;
    const m_dS2 = 6 * k_m * k_m * m_;
    const s_dS2 = 6 * k_s * k_s * s_;
    const f2 = wl * l + wm * m + ws * s;
    const f1 = wl * l_dS + wm * m_dS + ws * s_dS;
    const f22 = wl * l_dS2 + wm * m_dS2 + ws * s_dS2;
    S = S - f2 * f1 / (f1 * f1 - 0.5 * f2 * f22);
    return S;
  }
  function findCuspSRGB(a, b) {
    const S = maxSaturationSRGB(a, b);
    const lab = oklab(1, S * a, S * b);
    const xyzVal = toXYZ(lab);
    const rgb = fromXYZ5(xyzVal);
    const maxRGB = Math.max(rgb[0], rgb[1], rgb[2]);
    if (maxRGB <= 0)
      return [0, 0];
    const L_cusp = Math.cbrt(1 / maxRGB);
    const C_cusp = L_cusp * S;
    return [L_cusp, C_cusp];
  }
  function findCuspSRGBFromHueDeg(hDeg) {
    const h = wrapHueDeg(hDeg) * DEG_TO_RAD5;
    return findCuspSRGB(Math.cos(h), Math.sin(h));
  }
  var testCases10 = [
    {
      name: "cusp sRGB at hue 0 (pure red direction) has L_cusp \u2248 0.628",
      fn: () => findCuspSRGBFromHueDeg(29.2339)[0],
      // OKLCh hue of pure sRGB red
      expected: 0.6279,
      tolerance: 1e-3,
      source: "OKLab pure sRGB red has L = 0.6279554 \u2014 cusp at the matching hue should equal this"
    },
    {
      name: "cusp sRGB at hue 29.23 (pure red) has C_cusp \u2248 0.2576",
      fn: () => findCuspSRGBFromHueDeg(29.2339)[1],
      expected: 0.2576,
      tolerance: 5e-3,
      source: "OKLab pure sRGB red has C = 0.2576"
    },
    {
      name: "cusp sRGB at hue 264 (blue direction) has L_cusp \u2248 0.496",
      fn: () => findCuspSRGBFromHueDeg(264.05)[0],
      expected: 0.496,
      tolerance: 5e-3,
      source: "The cusp at blue hue is slightly higher L than pure-RGB blue (~0.45). Cusp is the max-chroma point, not the RGB primary point."
    }
  ];

  // lib/dist/gamut/oklch-peak.js
  var oklch_peak_exports = {};
  __export(oklch_peak_exports, {
    M_XYZ_TO_P3: () => M_XYZ_TO_P32,
    M_XYZ_TO_REC2020: () => M_XYZ_TO_REC20202,
    M_XYZ_TO_SRGB: () => M_XYZ_TO_SRGB2,
    inGamut: () => inGamut,
    peakC: () => peakC,
    peakC_P3: () => peakC_P3,
    peakC_Rec2020: () => peakC_Rec2020,
    peakC_sRGB: () => peakC_sRGB,
    peakL: () => peakL,
    peakLOverHue: () => peakLOverHue,
    peakL_P3: () => peakL_P3,
    peakL_Rec2020: () => peakL_Rec2020,
    peakL_sRGB: () => peakL_sRGB,
    testCases: () => testCases11
  });
  var M_XYZ_TO_SRGB2 = [
    [3.24096994, -1.53738318, -0.49861076],
    [-0.96924364, 1.8759675, 0.04155506],
    [0.05563008, -0.20397696, 1.05697151]
  ];
  var M_XYZ_TO_P32 = [
    [2.49349691, -0.93138362, -0.40271078],
    [-0.82948897, 1.76266406, 0.02362469],
    [0.03584583, -0.07617239, 0.95688452]
  ];
  var M_XYZ_TO_REC20202 = [
    [1.71665119, -0.35567078, -0.25336628],
    [-0.66668435, 1.61648124, 0.01576855],
    [0.01763986, -0.04277061, 0.94210312]
  ];
  function oklchToLinearRGB(oklch2, toRGB) {
    const [L, C5, hDeg] = oklch2;
    const hRad = hDeg * Math.PI / 180;
    const lab = [L, C5 * Math.cos(hRad), C5 * Math.sin(hRad)];
    const xyz2 = toXYZ(lab);
    return mulMat3Vec3(toRGB, xyz2);
  }
  function inGamut(rgb, epsilon = 0) {
    return rgb[0] >= -epsilon && rgb[0] <= 1 + epsilon && rgb[1] >= -epsilon && rgb[1] <= 1 + epsilon && rgb[2] >= -epsilon && rgb[2] <= 1 + epsilon;
  }
  function peakL(C5, hDeg, toRGB, iterations = 32) {
    const h = wrapHueDeg(hDeg);
    let lo = 0;
    let hi = 1;
    for (let i = 0; i < iterations; i++) {
      const mid = (lo + hi) / 2;
      const rgb = oklchToLinearRGB([mid, C5, h], toRGB);
      if (inGamut(rgb))
        lo = mid;
      else
        hi = mid;
    }
    return lo;
  }
  function peakC(L, hDeg, toRGB, iterations = 32, cMax = 0.4) {
    const h = wrapHueDeg(hDeg);
    let lo = 0;
    let hi = cMax;
    for (let i = 0; i < iterations; i++) {
      const mid = (lo + hi) / 2;
      const rgb = oklchToLinearRGB([L, mid, h], toRGB);
      if (inGamut(rgb))
        lo = mid;
      else
        hi = mid;
    }
    return lo;
  }
  function peakLOverHue(C5, toRGB, hueSteps = 720) {
    let bestL = 0;
    let bestH = 0;
    for (let i = 0; i < hueSteps; i++) {
      const h = i / hueSteps * 360;
      const L = peakL(C5, h, toRGB);
      if (L > bestL) {
        bestL = L;
        bestH = h;
      }
    }
    return { L: bestL, hDeg: bestH };
  }
  var peakL_sRGB = (C5, hDeg) => peakL(C5, hDeg, M_XYZ_TO_SRGB2);
  var peakL_P3 = (C5, hDeg) => peakL(C5, hDeg, M_XYZ_TO_P32);
  var peakL_Rec2020 = (C5, hDeg) => peakL(C5, hDeg, M_XYZ_TO_REC20202);
  var peakC_sRGB = (L, hDeg) => peakC(L, hDeg, M_XYZ_TO_SRGB2);
  var peakC_P3 = (L, hDeg) => peakC(L, hDeg, M_XYZ_TO_P32);
  var peakC_Rec2020 = (L, hDeg) => peakC(L, hDeg, M_XYZ_TO_REC20202, 32, 0.5);
  var testCases11 = [
    {
      name: "peakL_sRGB(C=0, h=0) \u2248 1 (achromatic)",
      fn: () => peakL_sRGB(0, 0),
      expected: 1,
      tolerance: 1e-3,
      source: "C=0 \u2192 achromatic \u2192 peak L is 1 (sRGB white) \u2014 binary search lands just below 1 due to float drift in OKLCH\u2192RGB"
    },
    {
      name: "peakC_sRGB(L=1, h=0) = 0 (white point)",
      fn: () => peakC_sRGB(1, 0),
      expected: 0,
      tolerance: 1e-6,
      source: "L=1 \u2192 white point \u2192 peak C is 0"
    },
    {
      name: "peakC_sRGB(L=0, h=0) = 0 (black point)",
      fn: () => peakC_sRGB(0, 0),
      expected: 0,
      tolerance: 1e-6,
      source: "L=0 \u2192 black point \u2192 peak C is 0"
    },
    {
      name: "peakL_sRGB(C=0.1, h=29) is in [0, 1]",
      fn: () => {
        const L = peakL_sRGB(0.1, 29);
        return L >= 0 && L <= 1 ? 0 : 1;
      },
      expected: 0,
      tolerance: 0,
      source: "Peak lightness always lands in unit interval"
    },
    {
      name: "peakC_P3 wider than peakC_sRGB at red mid-tone",
      fn: () => {
        const cSRGB = peakC_sRGB(0.5, 29);
        const cP3 = peakC_P3(0.5, 29);
        return cP3 > cSRGB ? 0 : 1;
      },
      expected: 0,
      tolerance: 0,
      source: "P3 has wider gamut than sRGB \u2192 peak C should be larger"
    }
  ];

  // lib/dist/gamut/mapping.js
  var mapping_exports = {};
  __export(mapping_exports, {
    clipNaive: () => clipNaive,
    inGamutP3: () => inGamutP3,
    inGamutRec2020: () => inGamutRec2020,
    inGamutSRGB: () => inGamutSRGB,
    mapToGamutOklch: () => mapToGamutOklch,
    mapToP3: () => mapToP3,
    mapToRec2020: () => mapToRec2020,
    mapToSRGB: () => mapToSRGB,
    testCases: () => testCases12
  });
  var JND_OK = 0.02;
  var EPSILON = 1e-4;
  function oklchToLinearRGB2(c, toRGB) {
    const lab = toOKLab(c);
    const xyz2 = toXYZ(lab);
    return mulMat3Vec3(toRGB, xyz2);
  }
  function inGamutSRGB(c) {
    return inGamut(oklchToLinearRGB2(c, M_XYZ_TO_SRGB2));
  }
  function inGamutP3(c) {
    return inGamut(oklchToLinearRGB2(c, M_XYZ_TO_P32));
  }
  function inGamutRec2020(c) {
    return inGamut(oklchToLinearRGB2(c, M_XYZ_TO_REC20202));
  }
  function clipNaive(rgb) {
    return [
      Math.min(1, Math.max(0, rgb[0])),
      Math.min(1, Math.max(0, rgb[1])),
      Math.min(1, Math.max(0, rgb[2]))
    ];
  }
  function mapToGamutOklch(origin, toRGB, inGamutFn) {
    const [L, C5, hDeg] = origin;
    if (inGamutFn(origin))
      return origin;
    if (L >= 1)
      return oklch(1, 0, hDeg);
    if (L <= 0)
      return oklch(0, 0, hDeg);
    const naiveClipColor = clipFromOklch(origin, toRGB);
    if (deltaEOK(toOKLab(origin), toOKLab(naiveClipColor)) < JND_OK) {
      return naiveClipColor;
    }
    let min = 0;
    let max = C5;
    let minInGamut = true;
    while (max - min > EPSILON) {
      const chroma = (min + max) / 2;
      const current = oklch(L, chroma, hDeg);
      if (minInGamut && inGamutFn(current)) {
        min = chroma;
      } else {
        const clipped = clipFromOklch(current, toRGB);
        const E3 = deltaEOK(toOKLab(current), toOKLab(clipped));
        if (E3 < JND_OK) {
          if (JND_OK - E3 < EPSILON) {
            return clipped;
          }
          minInGamut = false;
          min = chroma;
        } else {
          max = chroma;
        }
      }
    }
    return oklch(L, min, hDeg);
  }
  function clipFromOklch(c, toRGB) {
    const rgb = oklchToLinearRGB2(c, toRGB);
    const clipped = clipNaive(rgb);
    let oklch2;
    if (toRGB === M_XYZ_TO_SRGB2) {
      oklch2 = fromXYZ2(toXYZ5(linearSRGB(clipped[0], clipped[1], clipped[2])));
    } else if (toRGB === M_XYZ_TO_P32) {
      oklch2 = fromXYZ2(toXYZ6(linearP3(clipped[0], clipped[1], clipped[2])));
    } else {
      oklch2 = fromXYZ2(toXYZ7(clipped));
    }
    return oklch2;
  }
  function mapToSRGB(c) {
    const mapped = mapToGamutOklch(c, M_XYZ_TO_SRGB2, inGamutSRGB);
    const rgb = oklchToLinearRGB2(mapped, M_XYZ_TO_SRGB2);
    const clipped = clipNaive(rgb);
    return linearSRGB(clipped[0], clipped[1], clipped[2]);
  }
  function mapToP3(c) {
    const mapped = mapToGamutOklch(c, M_XYZ_TO_P32, inGamutP3);
    const rgb = oklchToLinearRGB2(mapped, M_XYZ_TO_P32);
    const clipped = clipNaive(rgb);
    return linearP3(clipped[0], clipped[1], clipped[2]);
  }
  function mapToRec2020(c) {
    const mapped = mapToGamutOklch(c, M_XYZ_TO_REC20202, inGamutRec2020);
    const rgb = oklchToLinearRGB2(mapped, M_XYZ_TO_REC20202);
    const clipped = clipNaive(rgb);
    return clipped;
  }
  var testCases12 = [
    {
      name: "in-gamut sRGB red is unchanged",
      fn: () => {
        const c = oklch(0.6279554, 0.2576, 29.2339);
        const mapped = mapToSRGB(c);
        return Math.hypot(mapped[0] - 1, mapped[1] - 0, mapped[2] - 0);
      },
      expected: 0,
      tolerance: 0.01,
      source: "OKLCh pure sRGB red \u2192 unchanged through mapToSRGB"
    },
    {
      name: "out-of-gamut chroma reduced (very vivid red)",
      fn: () => {
        const c = oklch(0.6, 0.5, 29);
        const mapped = mapToSRGB(c);
        const allInRange = mapped[0] >= 0 && mapped[0] <= 1 && mapped[1] >= 0 && mapped[1] <= 1 && mapped[2] >= 0 && mapped[2] <= 1;
        return allInRange ? 0 : 1;
      },
      expected: 0,
      tolerance: 0,
      source: "Out-of-gamut input must land in [0, 1]^3 after mapping"
    },
    {
      name: "L \u2265 1 returns white in sRGB",
      fn: () => {
        const c = oklch(1.5, 0.3, 180);
        const mapped = mapToSRGB(c);
        return Math.hypot(mapped[0] - 1, mapped[1] - 1, mapped[2] - 1);
      },
      expected: 0,
      tolerance: 0.01,
      source: "L > 1 must clamp to ~white in target gamut (small float drift through OKLab cube-root is expected)"
    },
    {
      name: "L \u2264 0 returns black in sRGB",
      fn: () => {
        const c = oklch(-0.1, 0.3, 180);
        const mapped = mapToSRGB(c);
        return Math.hypot(mapped[0], mapped[1], mapped[2]);
      },
      expected: 0,
      tolerance: 1e-4,
      source: "L < 0 must clamp to black in target gamut"
    }
  ];

  // lib/dist/quantize/kmeans.js
  var kmeans_exports = {};
  __export(kmeans_exports, {
    quantize: () => quantize,
    quantizeFromXYZ: () => quantizeFromXYZ,
    testCases: () => testCases13
  });
  function distSquared(a, b) {
    const dL = a[0] - b[0];
    const dA = a[1] - b[1];
    const dB = a[2] - b[2];
    return dL * dL + dA * dA + dB * dB;
  }
  function nearestCentroidIndex(point, centroids) {
    let bestIdx = 0;
    let bestDist = distSquared(point, centroids[0]);
    for (let i = 1; i < centroids.length; i++) {
      const d = distSquared(point, centroids[i]);
      if (d < bestDist) {
        bestDist = d;
        bestIdx = i;
      }
    }
    return bestIdx;
  }
  function pickInitial(points, k, seed = 0) {
    let state = seed >>> 0;
    const rand = () => {
      state = state * 1664525 + 1013904223 >>> 0;
      return state / 4294967296;
    };
    const centroids = [];
    centroids.push(points[Math.floor(rand() * points.length)]);
    while (centroids.length < k) {
      const dists = points.map((p) => {
        let min = Infinity;
        for (const c of centroids) {
          const d = distSquared(p, c);
          if (d < min)
            min = d;
        }
        return min;
      });
      const total = dists.reduce((s, d) => s + d, 0);
      const target = rand() * total;
      let cum = 0;
      for (let i = 0; i < dists.length; i++) {
        cum += dists[i];
        if (cum >= target) {
          centroids.push(points[i]);
          break;
        }
      }
    }
    return centroids;
  }
  function quantize(points, opts) {
    const { k, maxIterations = 50, tolerance = 1e-6, seed = 0 } = opts;
    if (points.length < k) {
      throw new Error(`Cannot quantize ${points.length} points to ${k} clusters`);
    }
    let centroids = pickInitial(points, k, seed);
    let assignments = points.map((p) => nearestCentroidIndex(p, centroids));
    let iterations = 0;
    for (; iterations < maxIterations; iterations++) {
      const sums = centroids.map(() => [0, 0, 0]);
      const counts = new Array(k).fill(0);
      for (let p = 0; p < points.length; p++) {
        const idx = assignments[p];
        sums[idx][0] += points[p][0];
        sums[idx][1] += points[p][1];
        sums[idx][2] += points[p][2];
        counts[idx]++;
      }
      const newCentroids = sums.map((s, i) => {
        const c = counts[i] || 1;
        return oklab(s[0] / c, s[1] / c, s[2] / c);
      });
      let maxMovement = 0;
      for (let i = 0; i < k; i++) {
        const d = Math.sqrt(distSquared(centroids[i], newCentroids[i]));
        if (d > maxMovement)
          maxMovement = d;
      }
      centroids = newCentroids;
      const newAssignments = points.map((p) => nearestCentroidIndex(p, centroids));
      assignments = newAssignments;
      if (maxMovement < tolerance)
        break;
    }
    let error = 0;
    for (let p = 0; p < points.length; p++) {
      error += distSquared(points[p], centroids[assignments[p]]);
    }
    return { palette: centroids, assignments, error, iterations };
  }
  function quantizeFromXYZ(xyzPoints, opts) {
    const oklabPoints = xyzPoints.map((p) => fromXYZ(p));
    return quantize(oklabPoints, opts);
  }
  var testCases13 = [
    {
      name: "k-means: 2 well-separated clusters \u2192 2 centroids near input modes",
      fn: () => {
        const points = [];
        for (let i = 0; i < 10; i++) {
          points.push(oklab(0.2 + i * 1e-3, 0.05, 0.05));
          points.push(oklab(0.8 + i * 1e-3, -0.05, -0.05));
        }
        const { palette } = quantize(points, { k: 2, seed: 42 });
        const Ls = palette.map((p) => p[0]).sort((a, b) => a - b);
        const darkOK = Math.abs(Ls[0] - 0.205) < 0.01;
        const lightOK = Math.abs(Ls[1] - 0.805) < 0.01;
        return darkOK && lightOK ? 0 : 1;
      },
      expected: 0,
      tolerance: 0,
      source: "k-means must recover two well-separated input clusters"
    },
    {
      name: "k-means: deterministic with same seed",
      fn: () => {
        const points = [];
        for (let i = 0; i < 20; i++) {
          points.push(oklab(Math.sin(i) * 0.5 + 0.5, Math.cos(i) * 0.2, Math.sin(i * 2) * 0.2));
        }
        const r1 = quantize(points, { k: 3, seed: 42 });
        const r2 = quantize(points, { k: 3, seed: 42 });
        const diff = r1.palette.reduce((acc, c, i) => acc + Math.abs(c[0] - r2.palette[i][0]), 0);
        return diff;
      },
      expected: 0,
      tolerance: 1e-12,
      source: "Same seed must produce identical results"
    }
  ];

  // lib/dist/dithering/floyd-steinberg.js
  var floyd_steinberg_exports = {};
  __export(floyd_steinberg_exports, {
    ditherFloydSteinberg: () => ditherFloydSteinberg,
    testCases: () => testCases14
  });
  function nearestPaletteIndex(point, palette) {
    let best = 0;
    let bestDist = Infinity;
    for (let i = 0; i < palette.length; i++) {
      const dL = point[0] - palette[i][0];
      const dA = point[1] - palette[i][1];
      const dB = point[2] - palette[i][2];
      const d = dL * dL + dA * dA + dB * dB;
      if (d < bestDist) {
        bestDist = d;
        best = i;
      }
    }
    return best;
  }
  function ditherFloydSteinberg(source, palette) {
    const H = source.length;
    const W = source[0].length;
    const buf = source.map((row) => row.map((c) => oklab(c[0], c[1], c[2])));
    const indices = [];
    const dithered = [];
    for (let y = 0; y < H; y++) {
      const idxRow = [];
      const dRow = [];
      for (let x = 0; x < W; x++) {
        const current = buf[y][x];
        const idx = nearestPaletteIndex(current, palette);
        const nearest = palette[idx];
        idxRow.push(idx);
        dRow.push(nearest);
        const errL = current[0] - nearest[0];
        const errA = current[1] - nearest[1];
        const errB = current[2] - nearest[2];
        const diffuse = (yy, xx, weight) => {
          if (yy < 0 || yy >= H || xx < 0 || xx >= W)
            return;
          buf[yy][xx] = oklab(buf[yy][xx][0] + errL * weight, buf[yy][xx][1] + errA * weight, buf[yy][xx][2] + errB * weight);
        };
        diffuse(y, x + 1, 7 / 16);
        diffuse(y + 1, x - 1, 3 / 16);
        diffuse(y + 1, x, 5 / 16);
        diffuse(y + 1, x + 1, 1 / 16);
      }
      indices.push(idxRow);
      dithered.push(dRow);
    }
    return { indices, dithered };
  }
  var testCases14 = [
    {
      name: "Floyd-Steinberg with 1-color palette returns that color everywhere",
      fn: () => {
        const source = [
          [oklab(0.5, 0.1, 0.1), oklab(0.6, 0, 0.2)],
          [oklab(0.3, 0.2, -0.1), oklab(0.7, -0.1, 0)]
        ];
        const palette = [oklab(0.5, 0, 0)];
        const { indices } = ditherFloydSteinberg(source, palette);
        for (const row of indices)
          for (const i of row)
            if (i !== 0)
              return 1;
        return 0;
      },
      expected: 0,
      tolerance: 0,
      source: "With only one palette color, every pixel maps to index 0"
    },
    {
      name: "Floyd-Steinberg: average error close to zero for balanced palette",
      fn: () => {
        const source = [];
        for (let y = 0; y < 8; y++) {
          const row = [];
          for (let x = 0; x < 8; x++) {
            const L = (y * 8 + x) / 63;
            row.push(oklab(L, 0, 0));
          }
          source.push(row);
        }
        const palette = [oklab(0, 0, 0), oklab(1, 0, 0)];
        const { dithered } = ditherFloydSteinberg(source, palette);
        let sumDithered = 0;
        let sumSource = 0;
        for (let y = 0; y < 8; y++) {
          for (let x = 0; x < 8; x++) {
            sumDithered += dithered[y][x][0];
            sumSource += source[y][x][0];
          }
        }
        return Math.abs(sumDithered / 64 - sumSource / 64);
      },
      expected: 0,
      tolerance: 0.05,
      source: "Floyd-Steinberg preserves average tone via error diffusion"
    }
  ];

  // lib/dist/convert.js
  var convert_exports = {};
  __export(convert_exports, {
    convert: () => convert,
    fromHub: () => fromHub,
    toHub: () => toHub
  });
  function convert(value, from, to) {
    return to.fromXYZ(from.toXYZ(value));
  }
  function toHub(value, from) {
    return from.toXYZ(value);
  }
  function fromHub(xyz2, to) {
    return to.fromXYZ(xyz2);
  }

  // lib/js/utils.js
  var utils_exports = {};
  __export(utils_exports, {
    clamp: () => clamp,
    copyToClipboard: () => copyToClipboard,
    el: () => el,
    fmt: () => fmt,
    fmtTuple: () => fmtTuple,
    fromHex: () => fromHex,
    raf: () => raf,
    setupCanvas: () => setupCanvas,
    toCssOklab: () => toCssOklab,
    toCssOklch: () => toCssOklch,
    toCssRgb: () => toCssRgb,
    toHex: () => toHex,
    toHexByte: () => toHexByte,
    wireFileDrop: () => wireFileDrop
  });
  var fmt = (x, n = 3) => {
    if (!Number.isFinite(x)) return "NaN";
    return Number(x).toFixed(n);
  };
  var fmtTuple = (t, n = 3) => "[" + Array.from(t).map((v) => fmt(v, n)).join(", ") + "]";
  var clamp = (x, min, max) => Math.max(min, Math.min(max, x));
  var toHexByte = (x) => {
    const v = Math.round(clamp(x, 0, 1) * 255);
    return v.toString(16).padStart(2, "0");
  };
  var toHex = (encoded) => "#" + toHexByte(encoded[0]) + toHexByte(encoded[1]) + toHexByte(encoded[2]);
  var fromHex = (hex) => {
    hex = hex.trim().replace(/^#/, "");
    if (hex.length === 3) hex = hex.split("").map((c) => c + c).join("");
    if (hex.length !== 6) return [0, 0, 0];
    return [
      parseInt(hex.substr(0, 2), 16) / 255,
      parseInt(hex.substr(2, 2), 16) / 255,
      parseInt(hex.substr(4, 2), 16) / 255
    ];
  };
  var toCssRgb = (encoded) => `rgb(${Math.round(encoded[0] * 255)} ${Math.round(encoded[1] * 255)} ${Math.round(encoded[2] * 255)})`;
  var toCssOklch = (oklch2) => `oklch(${fmt(oklch2[0], 4)} ${fmt(oklch2[1], 4)} ${fmt(oklch2[2], 2)})`;
  var toCssOklab = (oklab2) => `oklab(${fmt(oklab2[0], 4)} ${fmt(oklab2[1], 4)} ${fmt(oklab2[2], 4)})`;
  var el = (tag, attrs = {}, ...children) => {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") e.className = v;
      else if (k === "style" && typeof v === "object") Object.assign(e.style, v);
      else if (k.startsWith("on") && typeof v === "function") e.addEventListener(k.slice(2).toLowerCase(), v);
      else if (v !== void 0 && v !== null) e.setAttribute(k, v);
    }
    for (const c of children) {
      if (c == null) continue;
      e.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    }
    return e;
  };
  var raf = (fn) => {
    let pending = false;
    let lastArgs;
    return (...args) => {
      lastArgs = args;
      if (pending) return;
      pending = true;
      requestAnimationFrame(() => {
        pending = false;
        fn(...lastArgs);
      });
    };
  };
  var copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      return false;
    }
  };
  var setupCanvas = (canvas, w, h) => {
    const dpr = window.devicePixelRatio || 1;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";
    const ctx = canvas.getContext("2d");
    ctx.scale(dpr, dpr);
    return { ctx, w, h };
  };
  var wireFileDrop = (target, handler) => {
    if (!target) return;
    const setActive = (a) => target.classList.toggle("drop-active", a);
    target.addEventListener("dragover", (e) => {
      e.preventDefault();
      setActive(true);
    });
    target.addEventListener("dragenter", (e) => {
      e.preventDefault();
      setActive(true);
    });
    target.addEventListener("dragleave", () => setActive(false));
    target.addEventListener("dragend", () => setActive(false));
    target.addEventListener("drop", (e) => {
      e.preventDefault();
      setActive(false);
      const file = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
      if (file) handler(file);
    });
  };

  // lib/js/components/color-chip.js
  var ColorChip = class extends HTMLElement {
    static get observedAttributes() {
      return ["color", "label"];
    }
    connectedCallback() {
      this.render();
    }
    attributeChangedCallback() {
      this.render();
    }
    render() {
      const color = this.getAttribute("color") || "transparent";
      const label = this.getAttribute("label") || "";
      this.innerHTML = `
      <div class="chip-swatch" style="background: ${color};"></div>
      ${label ? `<div class="chip-label">${label}</div>` : ""}
    `;
    }
  };
  customElements.define("color-chip", ColorChip);

  // lib/js/components/gradient-strip.js
  var SPACE_LABELS = {
    "encoded-srgb": "Encoded sRGB (muddy mid-tones)",
    "linear-srgb": "Linear sRGB (too bright mid)",
    "cielab": "CIELAB (blue-purple drift)",
    "oklab": "OKLab (perceptually uniform)",
    "oklch": "OKLCh (preserves hue path)"
  };
  var GradientStrip = class extends HTMLElement {
    static get observedAttributes() {
      return ["from", "to", "space", "hue-path", "samples"];
    }
    connectedCallback() {
      this._build();
      this.render();
    }
    attributeChangedCallback() {
      if (this._canvas) this.render();
    }
    _build() {
      const space = this.getAttribute("space") || "oklab";
      const label = SPACE_LABELS[space] || space;
      this.innerHTML = `
      <div class="strip-label"><strong>${space}</strong><span>${label}</span></div>
      <canvas></canvas>
    `;
      this._canvas = this.querySelector("canvas");
    }
    render() {
      if (!this._canvas) return;
      const w = this.offsetWidth || 600;
      const h = 56;
      const samples = parseInt(this.getAttribute("samples") || "128", 10);
      const space = this.getAttribute("space") || "oklab";
      const huePath = this.getAttribute("hue-path") || "shorter";
      const fromHex_ = this.getAttribute("from") || "#000000";
      const toHex_ = this.getAttribute("to") || "#ffffff";
      const a_encoded = fromHex(fromHex_);
      const b_encoded = fromHex(toHex_);
      const a_linear = decode(a_encoded);
      const b_linear = decode(b_encoded);
      const a_xyz = toXYZ5(a_linear);
      const b_xyz = toXYZ5(b_linear);
      const colors = [];
      for (let i = 0; i < samples; i++) {
        const t = i / (samples - 1);
        let resultEncoded;
        switch (space) {
          case "encoded-srgb": {
            const rgb = lerpTuple(a_encoded, b_encoded, t);
            resultEncoded = rgb;
            break;
          }
          case "linear-srgb": {
            const rgb = lerpTuple(a_linear, b_linear, t);
            resultEncoded = encode(rgb);
            break;
          }
          case "cielab": {
            const a_lab = fromXYZ3(a_xyz);
            const b_lab = fromXYZ3(b_xyz);
            const mid = lerpCielab(a_lab, b_lab, t);
            const xyz_mid = toXYZ3(mid);
            const lin = fromXYZ5(xyz_mid);
            resultEncoded = encode(lin);
            break;
          }
          case "oklch": {
            const a_lch = fromXYZ2(a_xyz);
            const b_lch = fromXYZ2(b_xyz);
            const mid = lerpOklch(a_lch, b_lch, t, huePath);
            const mapped = mapToSRGB(mid);
            resultEncoded = encode(mapped);
            break;
          }
          case "oklab":
          default: {
            const a_lab = fromXYZ(a_xyz);
            const b_lab = fromXYZ(b_xyz);
            const mid = lerpOklab(a_lab, b_lab, t);
            const xyz_mid = toXYZ(mid);
            const lin = fromXYZ5(xyz_mid);
            resultEncoded = encode(lin);
            break;
          }
        }
        colors.push(resultEncoded);
      }
      const { ctx, w: cw, h: ch } = setupCanvas(this._canvas, w, h);
      const bw = cw / samples;
      for (let i = 0; i < samples; i++) {
        ctx.fillStyle = toCssRgb(colors[i]);
        ctx.fillRect(i * bw, 0, Math.ceil(bw) + 0.5, ch);
      }
    }
  };
  customElements.define("gradient-strip", GradientStrip);

  // lib/js/components/gamut-envelope.js
  var GAMUTS = {
    srgb: { matrix: M_XYZ_TO_SRGB2, color: "oklch(0.554 0.180 264)", label: "sRGB" },
    p3: { matrix: M_XYZ_TO_P32, color: "oklch(0.620 0.180 150)", label: "Display P3" },
    rec2020: { matrix: M_XYZ_TO_REC20202, color: "oklch(0.700 0.180  50)", label: "Rec.2020" }
  };
  var C_MAX = 0.4;
  var RES_CAP = 800;
  function readCssVar(name, fallback) {
    const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return v || fallback;
  }
  var GamutEnvelope = class extends HTMLElement {
    static get observedAttributes() {
      return ["hue", "show", "pick"];
    }
    connectedCallback() {
      this._build();
      this.render();
    }
    attributeChangedCallback() {
      if (this._canvas) this.render();
    }
    _build() {
      const showAttr = this.getAttribute("show") || "srgb,p3,rec2020";
      const showList = showAttr.split(",").map((s) => s.trim()).filter((s) => GAMUTS[s]);
      const legend = showList.map(
        (s) => `<span class="legend-item">
        <span class="legend-swatch" style="background:${GAMUTS[s].color}"></span>
        ${GAMUTS[s].label}
       </span>`
      ).join("");
      this.innerHTML = `
      <canvas tabindex="0" role="application" aria-label="OKLCh gamut envelope picker \u2014 click, drag, or use arrow keys to set lightness and chroma"></canvas>
      <div class="legend">${legend}</div>
    `;
      this._canvas = this.querySelector("canvas");
      this._dragging = false;
      this._canvas.addEventListener("pointerdown", (e) => {
        e.preventDefault();
        this._dragging = true;
        try {
          this._canvas.setPointerCapture(e.pointerId);
        } catch {
        }
        this._handlePoint(e);
      });
      this._canvas.addEventListener("pointermove", (e) => {
        if (this._dragging) this._handlePoint(e);
      });
      const endDrag = (e) => {
        this._dragging = false;
        try {
          this._canvas.releasePointerCapture(e.pointerId);
        } catch {
        }
      };
      this._canvas.addEventListener("pointerup", endDrag);
      this._canvas.addEventListener("pointercancel", endDrag);
      this._canvas.addEventListener("keydown", (e) => this._handleKey(e));
    }
    _handlePoint(e) {
      const rect = this._canvas.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = 1 - (e.clientY - rect.top) / rect.height;
      const L = Math.max(0, Math.min(1, y));
      const C5 = Math.max(0, Math.min(C_MAX, x * C_MAX));
      const hDeg = parseFloat(this.getAttribute("hue") || "29");
      this.dispatchEvent(new CustomEvent("pick", {
        detail: { L, C: C5, hDeg, oklch: [L, C5, hDeg] }
      }));
    }
    _handleKey(e) {
      if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(e.key)) return;
      e.preventDefault();
      const pickAttr = this.getAttribute("pick") || "0.5,0.1";
      const parts = pickAttr.split(",").map(Number);
      let L = parts[0], C5 = parts[1];
      const step = e.shiftKey ? 0.1 : 0.01;
      if (e.key === "ArrowLeft") C5 = Math.max(0, C5 - C_MAX * step);
      if (e.key === "ArrowRight") C5 = Math.min(C_MAX, C5 + C_MAX * step);
      if (e.key === "ArrowUp") L = Math.min(1, L + step);
      if (e.key === "ArrowDown") L = Math.max(0, L - step);
      const hDeg = parseFloat(this.getAttribute("hue") || "29");
      this.dispatchEvent(new CustomEvent("pick", {
        detail: { L, C: C5, hDeg, oklch: [L, C5, hDeg] }
      }));
    }
    render() {
      if (!this._canvas) return;
      const size = Math.min(this.offsetWidth || 500, 600);
      const { ctx, w, h } = setupCanvas(this._canvas, size, size);
      const hDeg = parseFloat(this.getAttribute("hue") || "29");
      const showList = (this.getAttribute("show") || "srgb,p3,rec2020").split(",").map((s) => s.trim()).filter((s) => GAMUTS[s]);
      ctx.fillStyle = readCssVar("--bg-card", "#ffffff");
      ctx.fillRect(0, 0, w, h);
      const dpr = window.devicePixelRatio || 1;
      const RES = Math.min(Math.round(w * dpr), RES_CAP);
      const tmp = document.createElement("canvas");
      tmp.width = RES;
      tmp.height = RES;
      const tmpCtx = tmp.getContext("2d");
      const imgData = tmpCtx.createImageData(RES, RES);
      const data = imgData.data;
      const DIM = { srgb: 1, p3: 0.62, rec2020: 0.38 };
      const inSrgb = showList.includes("srgb");
      const inP3 = showList.includes("p3");
      const inRec = showList.includes("rec2020");
      for (let py = 0; py < RES; py++) {
        for (let px = 0; px < RES; px++) {
          const L = 1 - py / (RES - 1);
          const C5 = px / (RES - 1) * C_MAX;
          const lab = toOKLab([L, C5, hDeg]);
          const xyz2 = toXYZ(lab);
          let dim = 0;
          if (inSrgb && inGamut(mulMat3Vec3(M_XYZ_TO_SRGB2, xyz2))) dim = DIM.srgb;
          else if (inP3 && inGamut(mulMat3Vec3(M_XYZ_TO_P32, xyz2))) dim = DIM.p3;
          else if (inRec && inGamut(mulMat3Vec3(M_XYZ_TO_REC20202, xyz2))) dim = DIM.rec2020;
          const i = (py * RES + px) * 4;
          if (dim === 0) {
            data[i + 3] = 0;
            continue;
          }
          const srgbLin = mulMat3Vec3(M_XYZ_TO_SRGB2, xyz2);
          const r = Math.max(0, Math.min(1, srgbLin[0]));
          const g = Math.max(0, Math.min(1, srgbLin[1]));
          const b = Math.max(0, Math.min(1, srgbLin[2]));
          const enc = encode([r, g, b]);
          data[i] = Math.round(enc[0] * 255 * dim);
          data[i + 1] = Math.round(enc[1] * 255 * dim);
          data[i + 2] = Math.round(enc[2] * 255 * dim);
          data[i + 3] = 255;
        }
      }
      tmpCtx.putImageData(imgData, 0, 0);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      ctx.drawImage(tmp, 0, 0, w, h);
      const BOUNDARY_SAMPLES = 96;
      for (const key of showList) {
        const { matrix, color } = GAMUTS[key];
        ctx.beginPath();
        const cMax = key === "rec2020" ? 0.5 : 0.4;
        for (let i = 0; i <= BOUNDARY_SAMPLES; i++) {
          const L = i / BOUNDARY_SAMPLES;
          const Cmax = peakC(L, hDeg, matrix, 28, cMax);
          const x = Cmax / C_MAX * w;
          const y = (1 - L) * h;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.stroke();
      }
      if (showList.includes("srgb")) {
        const cusp = findCuspSRGBFromHueDeg(hDeg);
        const cx = cusp[1] / C_MAX * w;
        const cy = (1 - cusp[0]) * h;
        ctx.beginPath();
        ctx.arc(cx, cy, 5, 0, Math.PI * 2);
        ctx.fillStyle = "#000";
        ctx.fill();
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 2;
        ctx.stroke();
      }
      const labelColor = readCssVar("--text-muted", "#888");
      ctx.fillStyle = labelColor;
      ctx.font = "11px ui-monospace, monospace";
      ctx.fillText("L=0", 4, h - 4);
      ctx.fillText("L=1", 4, 14);
      ctx.fillText("C=0", 4, h / 2 - 4);
      ctx.fillText(`C=${C_MAX}`, w - 36, h / 2 - 4);
      ctx.fillText(`h=${hDeg.toFixed(1)}\xB0`, w - 70, 14);
      const pick = this.getAttribute("pick");
      if (pick) {
        const parts = pick.split(",").map(Number);
        const pL = parts[0], pC = parts[1];
        const mx = pC / C_MAX * w;
        const my = (1 - pL) * h;
        ctx.beginPath();
        ctx.arc(mx, my, 7, 0, Math.PI * 2);
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 3;
        ctx.stroke();
        ctx.strokeStyle = "#000";
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    }
  };
  customElements.define("gamut-envelope", GamutEnvelope);

  // lib/js/components/transfer-curve.js
  var CURVES = {
    srgb: { encode: encodeComponent, color: "oklch(0.55 0.18 264)", label: "sRGB / Display P3" },
    rec2020: { encode: encodeComponent2, color: "oklch(0.62 0.18 150)", label: "Rec.2020 / Rec.709" },
    pq: { encode: encodeComponent3, color: "oklch(0.70 0.18  50)", label: "PQ (HDR)" },
    hlg: { encode: encodeComponent4, color: "oklch(0.57 0.22  29)", label: "HLG (HDR)" },
    adobergb: { encode: encodeComponent5, color: "oklch(0.55 0.18 300)", label: "Adobe RGB \u03B3=2.2" },
    prophoto: { encode: encodeComponent6, color: "oklch(0.55 0.18 200)", label: "ProPhoto \u03B3=1.8" }
  };
  var TransferCurve = class extends HTMLElement {
    static get observedAttributes() {
      return ["curves"];
    }
    connectedCallback() {
      this._build();
      this.render();
    }
    attributeChangedCallback() {
      if (this._canvas) this.render();
    }
    _build() {
      this.innerHTML = `<canvas></canvas><div class="legend" style="margin-top:var(--s-3);display:flex;gap:var(--s-3);flex-wrap:wrap;font-family:var(--font-mono);font-size:var(--text-xs);"></div>`;
      this._canvas = this.querySelector("canvas");
      this._legend = this.querySelector(".legend");
    }
    render() {
      const curvesList = (this.getAttribute("curves") || "srgb,rec2020").split(",").map((s) => s.trim().toLowerCase()).filter((s) => CURVES[s]);
      const size = Math.min(this.offsetWidth || 400, 500);
      const { ctx, w, h } = setupCanvas(this._canvas, size, size);
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--bg-card") || "#fff";
      ctx.fillRect(0, 0, w, h);
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--border") || "#eee";
      ctx.lineWidth = 1;
      for (let i = 1; i < 10; i++) {
        const p = i / 10 * w;
        ctx.beginPath();
        ctx.moveTo(p, 0);
        ctx.lineTo(p, h);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, p);
        ctx.lineTo(w, p);
        ctx.stroke();
      }
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-faint") || "#888";
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(0, h);
      ctx.lineTo(w, 0);
      ctx.stroke();
      ctx.setLineDash([]);
      for (const key of curvesList) {
        const { encode: encode7, color } = CURVES[key];
        ctx.strokeStyle = color;
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        const samples = w;
        for (let i = 0; i <= samples; i++) {
          const x = i / samples;
          const y = encode7(x);
          const px = x * w;
          const py = (1 - Math.max(0, Math.min(1, y))) * h;
          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.stroke();
      }
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted") || "#888";
      ctx.font = "11px ui-monospace, monospace";
      ctx.fillText("linear", 4, h - 4);
      ctx.fillText("encoded", 4, 12);
      this._legend.innerHTML = curvesList.map((k) => {
        const { color, label } = CURVES[k];
        return `<span style="display:flex;align-items:center;gap:4px;">
        <span style="display:inline-block;width:14px;height:3px;background:${color};border-radius:2px;"></span>
        ${label}
      </span>`;
      }).join("");
    }
  };
  customElements.define("transfer-curve", TransferCurve);

  // lib/js/components/contrast-readout.js
  function wcagTier(ratio) {
    if (ratio >= 7) return "AAA";
    if (ratio >= 4.5) return "AA";
    if (ratio >= 3) return "AA-large";
    return "fail";
  }
  function wcagPill(ratio) {
    const t = wcagTier(ratio);
    const cls = ratio >= 4.5 ? "pass" : ratio >= 3 ? "warn" : "fail";
    return `<span class="pill ${cls}">${t}</span>`;
  }
  function apcaPill(tier) {
    const goodTiers = ["optimal", "fluent-body", "body-minimum"];
    const cls = goodTiers.includes(tier) ? "pass" : tier === "insufficient" ? "fail" : "warn";
    return `<span class="pill ${cls}">${tier}</span>`;
  }
  var ContrastReadout = class extends HTMLElement {
    static get observedAttributes() {
      return ["text", "bg"];
    }
    connectedCallback() {
      this._build();
      this.render();
    }
    attributeChangedCallback() {
      if (this._mounted) this.render();
    }
    _build() {
      this.innerHTML = `
      <div class="preview" data-preview>
        The quick brown fox jumps.
        <div class="small">Aa Bb Cc 0123456789 \u2014 body text @ 16px / 400</div>
      </div>
      <div class="metrics">
        <div class="metric">
          <div class="metric-label">WCAG 2.2 contrast</div>
          <div class="metric-value" data-wcag>\u2014</div>
          <div class="metric-detail" data-wcag-detail>\u2014</div>
        </div>
        <div class="metric">
          <div class="metric-label">APCA L<sup>c</sup></div>
          <div class="metric-value" data-apca>\u2014</div>
          <div class="metric-detail" data-apca-detail>\u2014</div>
        </div>
      </div>
    `;
      this._mounted = true;
    }
    render() {
      const textHex = this.getAttribute("text") || "#000000";
      const bgHex = this.getAttribute("bg") || "#ffffff";
      const text = fromHex(textHex);
      const bg = fromHex(bgHex);
      const wcag = wcagContrast(text, bg);
      const apca = apcaContrast(text, bg);
      const tier = readabilityTier(apca);
      const preview = this.querySelector("[data-preview]");
      preview.style.background = bgHex;
      preview.style.color = textHex;
      this.querySelector("[data-wcag]").innerHTML = `${fmt(wcag, 2)}:1`;
      this.querySelector("[data-wcag-detail]").innerHTML = wcagPill(wcag) + " &nbsp; AA=4.5 \xB7 AAA=7";
      this.querySelector("[data-apca]").innerHTML = `${fmt(apca, 1)}`;
      this.querySelector("[data-apca-detail]").innerHTML = apcaPill(tier);
    }
  };
  customElements.define("contrast-readout", ContrastReadout);

  // lib/js/components/palette-display.js
  var PaletteDisplay = class extends HTMLElement {
    static get observedAttributes() {
      return ["colors"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._root) this.render();
    }
    set colors(arr) {
      this._colors = arr;
      if (this._root) this.render();
    }
    get colors() {
      return this._colors || [];
    }
    _mount() {
      this.innerHTML = `<div class="palette"></div>`;
      this._root = this.querySelector(".palette");
    }
    render() {
      let cols = this._colors;
      if (!cols) {
        const attr = this.getAttribute("colors");
        if (attr) {
          cols = attr.split(",").map((s) => fromHex(s.trim()));
        } else {
          cols = [];
        }
      }
      this._root.innerHTML = cols.map((c) => {
        const hex = toHex(c);
        return `<div class="palette-swatch">
        <div class="color" style="background:${hex}"></div>
        <div class="meta">${hex}</div>
      </div>`;
      }).join("");
    }
  };
  customElements.define("palette-display", PaletteDisplay);

  // lib/js/components/cvd-simulator.js
  var CVDSimulator = class extends HTMLElement {
    static get observedAttributes() {
      return ["type", "severity", "mode"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._canvas && this._sourceData) this.render();
    }
    _mount() {
      this.innerHTML = `
      <div class="cvd-host">
        <canvas></canvas>
        <p class="cvd-empty" style="color:var(--text-muted);font-size:var(--text-sm);">Drop or pick an image to see the simulation.</p>
      </div>`;
      this._canvas = this.querySelector("canvas");
      this._empty = this.querySelector(".cvd-empty");
    }
    setImage(image) {
      const work = document.createElement("canvas");
      work.width = image.naturalWidth || image.width;
      work.height = image.naturalHeight || image.height;
      const ctx = work.getContext("2d");
      ctx.drawImage(image, 0, 0);
      this._sourceData = ctx.getImageData(0, 0, work.width, work.height);
      this._sourceWidth = work.width;
      this._sourceHeight = work.height;
      if (this._empty) this._empty.style.display = "none";
      this.render();
    }
    render() {
      if (!this._canvas || !this._sourceData) return;
      const type = this.getAttribute("type") || "deuteranopia";
      const severity = parseFloat(this.getAttribute("severity") ?? "1") || 0;
      const mode = this.getAttribute("mode") || "split";
      const srcW = this._sourceWidth, srcH = this._sourceHeight;
      const M3 = simulationMatrix(type, severity);
      const simData = new ImageData(srcW, srcH);
      const src = this._sourceData.data;
      const dst = simData.data;
      for (let i = 0; i < src.length; i += 4) {
        const r = src[i] / 255, g = src[i + 1] / 255, b = src[i + 2] / 255;
        const lin = decode([r, g, b]);
        const sim = mulMat3Vec3(M3, lin);
        const cs = [
          Math.max(0, Math.min(1, sim[0])),
          Math.max(0, Math.min(1, sim[1])),
          Math.max(0, Math.min(1, sim[2]))
        ];
        const enc = encode(cs);
        dst[i] = Math.round(enc[0] * 255);
        dst[i + 1] = Math.round(enc[1] * 255);
        dst[i + 2] = Math.round(enc[2] * 255);
        dst[i + 3] = src[i + 3];
      }
      const targetW = Math.min(900, this.offsetWidth || 900);
      const aspect = srcH / srcW;
      let canvW, canvH, drawW;
      if (mode === "split") {
        drawW = targetW / 2;
        canvW = targetW;
        canvH = drawW * aspect;
      } else {
        drawW = targetW;
        canvW = targetW;
        canvH = targetW * aspect;
      }
      const { ctx, w, h } = setupCanvas(this._canvas, canvW, canvH);
      const origCv = document.createElement("canvas");
      origCv.width = srcW;
      origCv.height = srcH;
      origCv.getContext("2d").putImageData(this._sourceData, 0, 0);
      const simCv = document.createElement("canvas");
      simCv.width = srcW;
      simCv.height = srcH;
      simCv.getContext("2d").putImageData(simData, 0, 0);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      if (mode === "split") {
        ctx.drawImage(origCv, 0, 0, drawW, h);
        ctx.drawImage(simCv, drawW, 0, drawW, h);
        ctx.strokeStyle = "rgba(255,255,255,0.6)";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(drawW, 0);
        ctx.lineTo(drawW, h);
        ctx.stroke();
        ctx.fillStyle = "rgba(0,0,0,0.6)";
        ctx.fillRect(4, 4, 78, 18);
        ctx.fillRect(drawW + 4, 4, 130, 18);
        ctx.fillStyle = "#fff";
        ctx.font = "11px ui-monospace, monospace";
        ctx.fillText("original", 8, 17);
        ctx.fillText(`${type} ${Math.round(severity * 100)}%`, drawW + 8, 17);
      } else {
        ctx.drawImage(simCv, 0, 0, w, h);
      }
    }
  };
  customElements.define("cvd-simulator", CVDSimulator);

  // lib/js/components/token-ramp.js
  var STEP_LABELS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950];
  var GAMUT_MATRIX = {
    srgb: M_XYZ_TO_SRGB2,
    p3: M_XYZ_TO_P32,
    rec2020: M_XYZ_TO_REC20202
  };
  function oklchToHex(L, C5, hDeg) {
    const lab = toOKLab([L, C5, hDeg]);
    const xyz2 = toXYZ(lab);
    const lin = fromXYZ5(xyz2);
    const clamped = [
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ];
    return toHex(encode(clamped));
  }
  var TokenRamp = class extends HTMLElement {
    static get observedAttributes() {
      return ["hue", "curve", "chroma", "target"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._root) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="ramp-host"></div>`;
      this._root = this.querySelector(".ramp-host");
    }
    render() {
      const hue = parseFloat(this.getAttribute("hue") ?? "264");
      const curve = this.getAttribute("curve") || "tailwind";
      const chromaAttr = this.getAttribute("chroma") || "auto";
      const target = this.getAttribute("target") || "srgb";
      const matrix = GAMUT_MATRIX[target] || M_XYZ_TO_SRGB2;
      let lStops;
      if (curve === "tailwind") {
        lStops = TAILWIND_V4_L_STOPS.slice();
      } else if (curve === "linear") {
        lStops = STEP_LABELS.map((_, i) => linearRamp(1 - i / (STEP_LABELS.length - 1), 0.13, 0.985));
      } else if (curve === "smoothstep") {
        lStops = STEP_LABELS.map((_, i) => smoothstepRamp(1 - i / (STEP_LABELS.length - 1), 0.13, 0.985));
      } else if (curve.startsWith("gamma-")) {
        const g = parseFloat(curve.slice(6)) || 1.5;
        lStops = STEP_LABELS.map((_, i) => gammaRamp(1 - i / (STEP_LABELS.length - 1), g, 0.13, 0.985));
      } else {
        lStops = TAILWIND_V4_L_STOPS.slice();
      }
      const rows = lStops.map((L, i) => {
        let C5;
        if (chromaAttr === "auto") {
          C5 = peakC(L, hue, matrix, 28, 0.4);
        } else {
          const fixed = parseFloat(chromaAttr) || 0;
          C5 = Math.min(fixed, peakC(L, hue, matrix, 24, 0.4));
        }
        const hex = oklchToHex(L, C5, hue);
        const css = toCssOklch([L, C5, hue]);
        return { step: STEP_LABELS[i], L, C: C5, hex, css };
      });
      this._root.innerHTML = rows.map((r) => `
      <div class="ramp-row" style="background:${r.hex};color:${r.L > 0.5 ? "#111" : "#fafafa"}">
        <div class="ramp-step">${r.step}</div>
        <div class="ramp-meta">
          <div class="ramp-hex">${r.hex}</div>
          <div class="ramp-css">${r.css}</div>
        </div>
        <div class="ramp-lc">L=${fmt(r.L, 3)} C=${fmt(r.C, 3)}</div>
      </div>
    `).join("");
    }
  };
  customElements.define("token-ramp", TokenRamp);

  // lib/js/components/chromaticity-diagram.js
  var SPECTRAL_LOCUS = [
    [380, 0.1741, 5e-3],
    [385, 0.174, 5e-3],
    [390, 0.1738, 49e-4],
    [395, 0.1736, 49e-4],
    [400, 0.1733, 48e-4],
    [405, 0.173, 48e-4],
    [410, 0.1726, 48e-4],
    [415, 0.1721, 48e-4],
    [420, 0.1714, 51e-4],
    [425, 0.1703, 58e-4],
    [430, 0.1689, 69e-4],
    [435, 0.1669, 86e-4],
    [440, 0.1644, 0.0109],
    [445, 0.1611, 0.0138],
    [450, 0.1566, 0.0177],
    [455, 0.151, 0.0227],
    [460, 0.144, 0.0297],
    [465, 0.1355, 0.0399],
    [470, 0.1241, 0.0578],
    [475, 0.1096, 0.0868],
    [480, 0.0913, 0.1327],
    [485, 0.0687, 0.2007],
    [490, 0.0454, 0.295],
    [495, 0.0235, 0.4127],
    [500, 82e-4, 0.5384],
    [505, 39e-4, 0.6548],
    [510, 0.0139, 0.7502],
    [515, 0.0389, 0.812],
    [520, 0.0743, 0.8338],
    [525, 0.1142, 0.8262],
    [530, 0.1547, 0.8059],
    [535, 0.1929, 0.7816],
    [540, 0.2296, 0.7543],
    [545, 0.2658, 0.7243],
    [550, 0.3016, 0.6923],
    [555, 0.3373, 0.6589],
    [560, 0.3731, 0.6245],
    [565, 0.4087, 0.5896],
    [570, 0.4441, 0.5547],
    [575, 0.4788, 0.5202],
    [580, 0.5125, 0.4866],
    [585, 0.5448, 0.4544],
    [590, 0.5752, 0.4242],
    [595, 0.6029, 0.3965],
    [600, 0.627, 0.3725],
    [605, 0.6482, 0.3514],
    [610, 0.6658, 0.334],
    [615, 0.6801, 0.3197],
    [620, 0.6915, 0.3083],
    [625, 0.7006, 0.2993],
    [630, 0.7079, 0.292],
    [635, 0.714, 0.2859],
    [640, 0.719, 0.2809],
    [645, 0.723, 0.277],
    [650, 0.726, 0.274],
    [655, 0.7283, 0.2717],
    [660, 0.73, 0.27],
    [665, 0.7311, 0.2689],
    [670, 0.732, 0.268],
    [675, 0.7327, 0.2673],
    [680, 0.7334, 0.2666],
    [685, 0.734, 0.266],
    [690, 0.7344, 0.2656],
    [695, 0.7346, 0.2654],
    [700, 0.7347, 0.2653]
  ];
  var GAMUTS2 = {
    srgb: { name: "sRGB", color: "oklch(0.554 0.180 264)", tri: [[0.64, 0.33], [0.3, 0.6], [0.15, 0.06]] },
    p3: { name: "Display P3", color: "oklch(0.620 0.180 150)", tri: [[0.68, 0.32], [0.265, 0.69], [0.15, 0.06]] },
    rec2020: { name: "Rec.2020", color: "oklch(0.700 0.180  50)", tri: [[0.708, 0.292], [0.17, 0.797], [0.131, 0.046]] },
    adobergb: { name: "Adobe RGB", color: "oklch(0.554 0.180 300)", tri: [[0.64, 0.33], [0.21, 0.71], [0.15, 0.06]] },
    prophoto: { name: "ProPhoto", color: "oklch(0.620 0.180 200)", tri: [[0.7347, 0.2653], [0.1596, 0.8404], [0.0366, 1e-4]] }
  };
  var WHITE_POINTS = [
    { name: "D65", x: 0.31272, y: 0.32903 },
    { name: "D50", x: 0.34567, y: 0.3585 },
    { name: "D55", x: 0.33242, y: 0.34743 },
    { name: "A", x: 0.44757, y: 0.40745 }
  ];
  var X_RANGE = [0, 0.8];
  var Y_RANGE = [0, 0.9];
  function xToPx(x, w) {
    return (x - X_RANGE[0]) / (X_RANGE[1] - X_RANGE[0]) * w;
  }
  function yToPx(y, h) {
    return h - (y - Y_RANGE[0]) / (Y_RANGE[1] - Y_RANGE[0]) * h;
  }
  var ChromaticityDiagram = class extends HTMLElement {
    static get observedAttributes() {
      return ["show", "pick"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._canvas) this.render();
    }
    _mount() {
      this.innerHTML = `<canvas tabindex="0" role="application" aria-label="CIE xy chromaticity diagram \u2014 click, drag, or use arrow keys to pick a chromaticity"></canvas>`;
      this._canvas = this.querySelector("canvas");
      this._canvas.addEventListener("keydown", (e) => this._handleKey(e));
      this._dragging = false;
      this._canvas.addEventListener("pointerdown", (e) => {
        e.preventDefault();
        this._dragging = true;
        try {
          this._canvas.setPointerCapture(e.pointerId);
        } catch {
        }
        this._handlePoint(e);
      });
      this._canvas.addEventListener("pointermove", (e) => {
        if (this._dragging) this._handlePoint(e);
      });
      const endDrag = (e) => {
        this._dragging = false;
        try {
          this._canvas.releasePointerCapture(e.pointerId);
        } catch {
        }
      };
      this._canvas.addEventListener("pointerup", endDrag);
      this._canvas.addEventListener("pointercancel", endDrag);
    }
    _handlePoint(e) {
      const rect = this._canvas.getBoundingClientRect();
      const px = (e.clientX - rect.left) / rect.width;
      const py = 1 - (e.clientY - rect.top) / rect.height;
      const x = X_RANGE[0] + px * (X_RANGE[1] - X_RANGE[0]);
      const y = Y_RANGE[0] + py * (Y_RANGE[1] - Y_RANGE[0]);
      if (x <= 0 || y <= 0 || 1 - x - y <= -0.05) return;
      const xyz2 = toXYZ14([x, y, 1]);
      this.dispatchEvent(new CustomEvent("pick", {
        detail: { x, y, Y: 1, xyz: xyz2 }
      }));
    }
    _handleKey(e) {
      if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(e.key)) return;
      e.preventDefault();
      const pickAttr = this.getAttribute("pick") || "0.3127,0.3290";
      const parts = pickAttr.split(",").map(Number);
      let x = parts[0], y = parts[1];
      const step = e.shiftKey ? 0.05 : 5e-3;
      if (e.key === "ArrowLeft") x = Math.max(X_RANGE[0], x - step);
      if (e.key === "ArrowRight") x = Math.min(X_RANGE[1], x + step);
      if (e.key === "ArrowUp") y = Math.min(Y_RANGE[1], y + step);
      if (e.key === "ArrowDown") y = Math.max(Y_RANGE[0], y - step);
      if (x <= 0 || y <= 0 || 1 - x - y <= -0.05) return;
      const xyz2 = toXYZ14([x, y, 1]);
      this.dispatchEvent(new CustomEvent("pick", {
        detail: { x, y, Y: 1, xyz: xyz2 }
      }));
    }
    render() {
      if (!this._canvas) return;
      const w0 = Math.min(this.offsetWidth || 640, 760);
      const h0 = Math.round(w0 * (Y_RANGE[1] / X_RANGE[1]));
      const { ctx, w, h } = setupCanvas(this._canvas, w0, h0);
      const showAttr = this.getAttribute("show") || "srgb,p3,rec2020";
      const showList = showAttr.split(",").map((s) => s.trim()).filter((k) => GAMUTS2[k]);
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--bg-elevated").trim() || "#222";
      ctx.fillRect(0, 0, w, h);
      const dpr = window.devicePixelRatio || 1;
      const RES = Math.min(Math.round(w * dpr), 800);
      const tmp = document.createElement("canvas");
      tmp.width = RES;
      tmp.height = RES;
      const tmpCtx = tmp.getContext("2d");
      const imgData = tmpCtx.createImageData(RES, RES);
      const data = imgData.data;
      const locusPolyXY = SPECTRAL_LOCUS.map((p) => [p[1], p[2]]);
      for (let py = 0; py < RES; py++) {
        for (let px = 0; px < RES; px++) {
          const x = X_RANGE[0] + px / RES * (X_RANGE[1] - X_RANGE[0]);
          const y = Y_RANGE[1] - py / RES * (Y_RANGE[1] - Y_RANGE[0]);
          if (!pointInPolygon(x, y, locusPolyXY)) {
            data[(py * RES + px) * 4 + 3] = 0;
            continue;
          }
          const Y = 0.5;
          const xyz2 = toXYZ14([x, y, Y]);
          const lin = fromXYZ5(xyz2);
          const cs = [
            Math.max(0, Math.min(1, lin[0])),
            Math.max(0, Math.min(1, lin[1])),
            Math.max(0, Math.min(1, lin[2]))
          ];
          const enc = encode(cs);
          const i = (py * RES + px) * 4;
          data[i] = Math.round(enc[0] * 255);
          data[i + 1] = Math.round(enc[1] * 255);
          data[i + 2] = Math.round(enc[2] * 255);
          data[i + 3] = 255;
        }
      }
      tmpCtx.putImageData(imgData, 0, 0);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      ctx.drawImage(tmp, 0, 0, w, h);
      ctx.strokeStyle = "rgba(255,255,255,0.85)";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      SPECTRAL_LOCUS.forEach(([_nm, x, y], i) => {
        const px = xToPx(x, w);
        const py = yToPx(y, h);
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.closePath();
      ctx.stroke();
      for (const key of showList) {
        const { tri, color, name } = GAMUTS2[key];
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        tri.forEach(([x, y], i) => {
          const px = xToPx(x, w);
          const py = yToPx(y, h);
          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        });
        ctx.closePath();
        ctx.stroke();
        ctx.fillStyle = color;
        ctx.font = "11px ui-monospace, monospace";
        const lx = xToPx(tri[0][0], w);
        const ly = yToPx(tri[0][1], h);
        ctx.fillText(name, lx + 6, ly - 4);
      }
      for (const wp of WHITE_POINTS) {
        const px = xToPx(wp.x, w);
        const py = yToPx(wp.y, h);
        ctx.beginPath();
        ctx.arc(px, py, 3.5, 0, Math.PI * 2);
        ctx.fillStyle = "#fff";
        ctx.fill();
        ctx.strokeStyle = "#000";
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.fillStyle = "#fff";
        ctx.font = "10px ui-monospace, monospace";
        ctx.fillText(wp.name, px + 6, py + 4);
      }
      ctx.fillStyle = "rgba(255,255,255,0.7)";
      ctx.font = "9px ui-monospace, monospace";
      const WL_TICKS = [400, 470, 480, 490, 500, 520, 540, 560, 580, 600, 620, 700];
      for (const nm of WL_TICKS) {
        const sp = SPECTRAL_LOCUS.find((p) => p[0] === nm);
        if (!sp) continue;
        const px = xToPx(sp[1], w);
        const py = yToPx(sp[2], h);
        ctx.fillText(String(nm), px + 4, py - 2);
      }
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#999";
      ctx.font = "11px ui-monospace, monospace";
      ctx.fillText("x", w - 12, h - 6);
      ctx.fillText("y", 6, 14);
      const pick = this.getAttribute("pick");
      if (pick) {
        const parts = pick.split(",").map(Number);
        const px = xToPx(parts[0], w);
        const py = yToPx(parts[1], h);
        ctx.beginPath();
        ctx.arc(px, py, 7, 0, Math.PI * 2);
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 3;
        ctx.stroke();
        ctx.strokeStyle = "#000";
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    }
  };
  function pointInPolygon(x, y, poly) {
    let inside = false;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      const xi = poly[i][0], yi = poly[i][1];
      const xj = poly[j][0], yj = poly[j][1];
      const intersect = yi > y !== yj > y && x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi;
      if (intersect) inside = !inside;
    }
    return inside;
  }
  customElements.define("chromaticity-diagram", ChromaticityDiagram);

  // lib/js/components/gamut-strip.js
  function oklchToLinearSRGB(c) {
    const lab = toOKLab(c);
    const xyz2 = toXYZ(lab);
    return mulMat3Vec3(M_XYZ_TO_SRGB2, xyz2);
  }
  function clampLin(lin) {
    return [
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ];
  }
  function encodedToHex(enc) {
    return toHex(enc);
  }
  function strategyClip(oklch2) {
    const lin = oklchToLinearSRGB(oklch2);
    const clipped = clipNaive(lin);
    const enc = encode(clipped);
    const back = fromXYZ2(toXYZ5(clipped));
    return { hex: encodedToHex(enc), out: back };
  }
  function strategyChromaReduce(oklch2) {
    const mapped = mapToGamutOklch(oklch2, M_XYZ_TO_SRGB2, inGamutSRGB);
    const lin = oklchToLinearSRGB(mapped);
    const clipped = clipNaive(lin);
    const enc = encode(clipped);
    return { hex: encodedToHex(enc), out: mapped };
  }
  function strategyMinde(oklch2) {
    const [L, C5, h] = oklch2;
    const cusp = findCuspSRGBFromHueDeg(h);
    const cL = cusp[0], cC = cusp[1];
    const targetC = Math.min(cC, peakC(L, h, M_XYZ_TO_SRGB2, 28, 0.4));
    const reduction = C5 > 0 ? (C5 - targetC) / C5 : 0;
    const blend = Math.min(0.4, Math.max(0, reduction));
    const newL = L * (1 - blend) + cL * blend;
    const finalC = peakC(newL, h, M_XYZ_TO_SRGB2, 28, 0.4);
    const out = [newL, Math.min(targetC, finalC), h];
    const lin = oklchToLinearSRGB(out);
    const enc = encode(clampLin(lin));
    return { hex: encodedToHex(enc), out };
  }
  function strategyCuspProject(oklch2) {
    const [L, C5, h] = oklch2;
    const cusp = findCuspSRGBFromHueDeg(h);
    const cL = cusp[0], cC = cusp[1];
    let lo = 0, hi = 1;
    for (let i = 0; i < 32; i++) {
      const t2 = (lo + hi) / 2;
      const Lt = L + (cL - L) * t2;
      const Ct = C5 + (cC - C5) * t2;
      if (inGamutSRGB([Lt, Ct, h])) hi = t2;
      else lo = t2;
    }
    const t = hi;
    const out = [L + (cL - L) * t, C5 + (cC - C5) * t, h];
    const lin = oklchToLinearSRGB(out);
    const enc = encode(clampLin(lin));
    return { hex: encodedToHex(enc), out };
  }
  var STRATEGIES = [
    { id: "clip", label: "naive clip", note: "clamp each linear-RGB channel \u2014 shifts hue", fn: strategyClip },
    { id: "css4", label: "CSS Color 4", note: "reduce chroma in OKLCh \u2014 W3C standard", fn: strategyChromaReduce },
    { id: "minde", label: "min-\u0394E blend", note: "reduce chroma + nudge L toward cusp", fn: strategyMinde },
    { id: "cusp", label: "cusp projection", note: "line from source toward gamut cusp", fn: strategyCuspProject }
  ];
  var GamutStrip = class extends HTMLElement {
    static get observedAttributes() {
      return ["oklch", "target"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._root) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="gamut-strip"></div>`;
      this._root = this.querySelector(".gamut-strip");
    }
    render() {
      const attr = this.getAttribute("oklch") || "0.7,0.35,29";
      const parts = attr.split(",").map((s) => parseFloat(s.trim()));
      const source = [parts[0] || 0.7, parts[1] || 0.35, parts[2] || 29];
      const sourceInGamut = inGamutSRGB(source);
      this._root.innerHTML = STRATEGIES.map((s) => {
        const { hex, out } = s.fn(source);
        return `
        <div class="gamut-cell">
          <div class="gamut-swatch" style="background:${hex}"></div>
          <div class="gamut-info">
            <div class="gamut-label">${s.label}</div>
            <div class="gamut-note">${s.note}</div>
            <div class="gamut-result">
              <code>${toCssOklch(out)}</code><br>
              <code>${hex}</code>
            </div>
          </div>
        </div>
      `;
      }).join("");
      if (sourceInGamut) {
        this._root.insertAdjacentHTML(
          "beforeend",
          `<p class="gamut-already-in"><strong>Note:</strong> this color is already in sRGB \u2014 all strategies converge.</p>`
        );
      }
    }
  };
  customElements.define("gamut-strip", GamutStrip);

  // lib/js/components/hue-wheel.js
  var RING_COUNT = 3;
  var HUE_STEPS = 180;
  function oklchToHex2(L, C5, hDeg) {
    const lab = toOKLab([L, C5, hDeg]);
    const xyz2 = toXYZ(lab);
    const lin = fromXYZ5(xyz2);
    const clamped = [
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ];
    const enc = encode(clamped);
    return [
      Math.round(enc[0] * 255),
      Math.round(enc[1] * 255),
      Math.round(enc[2] * 255)
    ];
  }
  function hslToHex(h, s, l) {
    const xyz2 = toXYZ8([h, s, l]);
    const lin = fromXYZ5(xyz2);
    const clamped = [
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ];
    const enc = encode(clamped);
    return [
      Math.round(enc[0] * 255),
      Math.round(enc[1] * 255),
      Math.round(enc[2] * 255)
    ];
  }
  function hctToHex(h, c, t) {
    const xyz2 = toXYZ11([h, c, t]);
    const lin = fromXYZ5(xyz2);
    const clamped = [
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ];
    const enc = encode(clamped);
    return [
      Math.round(enc[0] * 255),
      Math.round(enc[1] * 255),
      Math.round(enc[2] * 255)
    ];
  }
  var HueWheel = class extends HTMLElement {
    static get observedAttributes() {
      return ["l", "c"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._canvas) this.render();
    }
    _mount() {
      this.innerHTML = `<canvas></canvas>
      <div class="wheel-legend" style="display:flex;gap:1rem;font-size:var(--text-xs);font-family:var(--font-mono);justify-content:center;margin-top:var(--s-3);color:var(--text-muted)">
        <span><span style="color:oklch(0.554 0.18 264)">\u25CF</span> OKLCh (outer)</span>
        <span><span style="color:oklch(0.620 0.18 150)">\u25CF</span> HCT (middle)</span>
        <span><span style="color:oklch(0.700 0.18 50)">\u25CF</span> HSL (inner)</span>
      </div>`;
      this._canvas = this.querySelector("canvas");
    }
    render() {
      if (!this._canvas) return;
      const L = parseFloat(this.getAttribute("l") ?? "0.65");
      const Cok = parseFloat(this.getAttribute("c") ?? "0.15");
      const size = Math.min(this.offsetWidth || 480, 560);
      const { ctx, w, h } = setupCanvas(this._canvas, size, size);
      ctx.clearRect(0, 0, w, h);
      const cx = w / 2, cy = h / 2;
      const ringOuter = Math.min(w, h) * 0.46;
      const ringInner = ringOuter * 0.4;
      const ringThickness = (ringOuter - ringInner) / RING_COUNT;
      const tau = Math.PI * 2;
      const sliceAngle = tau / HUE_STEPS;
      for (let r = 0; r < RING_COUNT; r++) {
        const rOut = ringOuter - r * ringThickness;
        const rIn = rOut - ringThickness + 1;
        for (let i = 0; i < HUE_STEPS; i++) {
          const hueDeg = i / HUE_STEPS * 360;
          let rgb;
          if (r === 0) {
            rgb = oklchToHex2(L, Cok, hueDeg);
          } else if (r === 1) {
            rgb = hctToHex(hueDeg, 50, L * 100);
          } else {
            rgb = hslToHex(hueDeg, 0.65, L);
          }
          ctx.fillStyle = `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
          const a0 = -Math.PI / 2 + i * sliceAngle;
          const a1 = a0 + sliceAngle + 5e-3;
          ctx.beginPath();
          ctx.moveTo(cx + Math.cos(a0) * rIn, cy + Math.sin(a0) * rIn);
          ctx.arc(cx, cy, rOut, a0, a1);
          ctx.lineTo(cx + Math.cos(a1) * rIn, cy + Math.sin(a1) * rIn);
          ctx.arc(cx, cy, rIn, a1, a0, true);
          ctx.closePath();
          ctx.fill();
        }
      }
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      ctx.font = "12px ui-monospace, monospace";
      ctx.textAlign = "center";
      ctx.fillText(`L = ${L.toFixed(2)}`, cx, cy - 4);
      ctx.fillText(`C = ${Cok.toFixed(2)}`, cx, cy + 14);
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      ctx.font = "10px ui-monospace, monospace";
      ctx.textAlign = "center";
      for (let deg = 0; deg < 360; deg += 30) {
        const a = -Math.PI / 2 + deg / 360 * tau;
        const lx = cx + Math.cos(a) * (ringOuter + 12);
        const ly = cy + Math.sin(a) * (ringOuter + 12) + 4;
        ctx.fillText(`${deg}\xB0`, lx, ly);
      }
    }
  };
  customElements.define("hue-wheel", HueWheel);

  // lib/js/components/image-histograms.js
  var HUE_BINS = 72;
  var L_BINS = 32;
  var SAMPLE_STEP = 4;
  var ImageHistograms = class extends HTMLElement {
    connectedCallback() {
      this._mount();
    }
    _mount() {
      this.innerHTML = `
      <div class="hist-host">
        <div class="hist-row">
          <canvas class="hist-hue"></canvas>
          <canvas class="hist-l"></canvas>
        </div>
        <div class="hist-stats" style="font-family:var(--font-mono); font-size:var(--text-xs); color:var(--text-muted); margin-top:var(--s-3); display:grid; grid-template-columns:repeat(2, 1fr); gap:var(--s-2);"></div>
      </div>`;
      this._hueCanvas = this.querySelector(".hist-hue");
      this._lCanvas = this.querySelector(".hist-l");
      this._stats = this.querySelector(".hist-stats");
    }
    setImage(image) {
      if (!this._hueCanvas) this._mount();
      const work = document.createElement("canvas");
      const W = image.naturalWidth || image.width;
      const H = image.naturalHeight || image.height;
      work.width = W;
      work.height = H;
      work.getContext("2d").drawImage(image, 0, 0);
      const data = work.getContext("2d").getImageData(0, 0, W, H).data;
      const hueBins = new Array(HUE_BINS).fill(0);
      const lBins = new Array(L_BINS).fill(0);
      let totalC = 0, samples = 0;
      for (let i = 0; i < data.length; i += 4 * SAMPLE_STEP) {
        const r = data[i] / 255, g = data[i + 1] / 255, b = data[i + 2] / 255;
        const lin = decode([r, g, b]);
        const xyz2 = toXYZ5(lin);
        const lch = fromXYZ2(xyz2);
        const L = lch[0], C5 = lch[1], hDeg = lch[2];
        const hb = Math.floor(hDeg / 360 * HUE_BINS) % HUE_BINS;
        hueBins[hb] += C5;
        const lb = Math.min(L_BINS - 1, Math.max(0, Math.floor(L * L_BINS)));
        lBins[lb] += 1;
        totalC += C5;
        samples++;
      }
      this._renderHueHist(hueBins);
      this._renderLHist(lBins);
      const avgC = samples > 0 ? totalC / samples : 0;
      this._stats.innerHTML = `
      <div>sampled pixels: <strong>${samples}</strong></div>
      <div>avg OKLCh chroma: <strong>${fmt(avgC, 3)}</strong></div>
    `;
    }
    _renderHueHist(bins) {
      const size = Math.min(this._hueCanvas.offsetWidth || 280, 360);
      const { ctx, w, h } = setupCanvas(this._hueCanvas, size, size);
      ctx.clearRect(0, 0, w, h);
      const cx = w / 2, cy = h / 2;
      const rIn = Math.min(w, h) * 0.22;
      const rOutMax = Math.min(w, h) * 0.46;
      const max = Math.max(...bins, 1e-9);
      const tau = Math.PI * 2;
      for (let i = 0; i < HUE_BINS; i++) {
        const hueDeg = i / HUE_BINS * 360;
        const t = bins[i] / max;
        const rOut = rIn + (rOutMax - rIn) * t;
        const a0 = -Math.PI / 2 + i / HUE_BINS * tau;
        const a1 = a0 + tau / HUE_BINS;
        const lab = toOKLab([0.65, 0.15, hueDeg]);
        const xyz2 = toXYZ(lab);
        const lin = fromXYZ5(xyz2);
        const cs = [
          Math.max(0, Math.min(1, lin[0])),
          Math.max(0, Math.min(1, lin[1])),
          Math.max(0, Math.min(1, lin[2]))
        ];
        const enc = encode(cs);
        ctx.fillStyle = `rgb(${Math.round(enc[0] * 255)},${Math.round(enc[1] * 255)},${Math.round(enc[2] * 255)})`;
        ctx.beginPath();
        ctx.moveTo(cx + Math.cos(a0) * rIn, cy + Math.sin(a0) * rIn);
        ctx.arc(cx, cy, rOut, a0, a1);
        ctx.lineTo(cx + Math.cos(a1) * rIn, cy + Math.sin(a1) * rIn);
        ctx.arc(cx, cy, rIn, a1, a0, true);
        ctx.closePath();
        ctx.fill();
      }
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--border").trim() || "#666";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(cx, cy, rOutMax, 0, tau);
      ctx.stroke();
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      ctx.font = "11px ui-monospace, monospace";
      ctx.textAlign = "center";
      ctx.fillText("hue \xD7 chroma", cx, cy + 4);
    }
    _renderLHist(bins) {
      const wPx = this._lCanvas.offsetWidth || 280;
      const hPx = Math.round(wPx * 0.7);
      const { ctx, w, h } = setupCanvas(this._lCanvas, wPx, hPx);
      ctx.clearRect(0, 0, w, h);
      const max = Math.max(...bins, 1);
      const barW = w / L_BINS;
      for (let i = 0; i < L_BINS; i++) {
        const L = (i + 0.5) / L_BINS;
        const t = bins[i] / max;
        const barH = t * (h - 20);
        const gray = Math.round(encodeComponent(L) * 255);
        ctx.fillStyle = `rgb(${gray},${gray},${gray})`;
        ctx.fillRect(i * barW + 1, h - barH - 14, barW - 2, barH);
      }
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--border").trim() || "#666";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, h - 14);
      ctx.lineTo(w, h - 14);
      ctx.stroke();
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      ctx.font = "11px ui-monospace, monospace";
      ctx.textAlign = "left";
      ctx.fillText("L = 0", 2, h - 2);
      ctx.textAlign = "right";
      ctx.fillText("L = 1", w - 2, h - 2);
      ctx.textAlign = "center";
      ctx.fillText("lightness distribution", w / 2, h - 2);
    }
  };
  customElements.define("image-histograms", ImageHistograms);

  // lib/dist/pigment/kubelka-munk.js
  function reflectanceToKS(R) {
    if (R <= 0)
      return 1e6;
    if (R >= 1)
      return 0;
    return (1 - R) * (1 - R) / (2 * R);
  }
  function KSToReflectance(KS) {
    if (KS <= 0)
      return 1;
    return 1 + KS - Math.sqrt(KS * KS + 2 * KS);
  }
  function spectrumToKS(reflectance) {
    return reflectance.map(reflectanceToKS);
  }
  function KSToSpectrum(KS) {
    return KS.map(KSToReflectance);
  }
  function mix(spectrumA, spectrumB, concentrationA) {
    const cA = Math.max(0, Math.min(1, concentrationA));
    const cB = 1 - cA;
    const ksA = spectrumToKS(spectrumA);
    const ksB = spectrumToKS(spectrumB);
    const mixed = ksA.map((ks, i) => cA * ks + cB * ksB[i]);
    return KSToSpectrum(mixed);
  }

  // lib/dist/spectral/cmf.js
  var X_BAR_1931 = [
    1368e-6,
    4243e-6,
    0.01431,
    0.04351,
    0.13438,
    0.2839,
    0.34828,
    0.3362,
    0.2908,
    0.19536,
    0.09564,
    0.03201,
    49e-4,
    93e-4,
    0.06327,
    0.1655,
    0.2904,
    0.43345,
    0.5945,
    0.7621,
    0.9163,
    1.0263,
    1.0622,
    1.0026,
    0.85445,
    0.6424,
    0.4479,
    0.2835,
    0.1649,
    0.0874,
    0.04677,
    0.0227,
    0.011359,
    579e-5,
    2899e-6,
    144e-5
  ];
  var Y_BAR_1931 = [
    39e-6,
    12e-5,
    396e-6,
    121e-5,
    4e-3,
    0.0116,
    0.023,
    0.038,
    0.06,
    0.09098,
    0.13902,
    0.20802,
    0.323,
    0.503,
    0.71,
    0.862,
    0.954,
    0.99495,
    0.995,
    0.952,
    0.87,
    0.757,
    0.631,
    0.503,
    0.381,
    0.265,
    0.175,
    0.107,
    0.061,
    0.032,
    0.017,
    821e-5,
    4102e-6,
    2091e-6,
    1047e-6,
    52e-5
  ];
  var Z_BAR_1931 = [
    645e-5,
    0.02005,
    0.06785,
    0.2074,
    0.6456,
    1.3856,
    1.74706,
    1.77211,
    1.6692,
    1.28764,
    0.81295,
    0.46518,
    0.272,
    0.1582,
    0.07825,
    0.04216,
    0.0203,
    875e-5,
    39e-4,
    21e-4,
    165e-5,
    11e-4,
    8e-4,
    34e-5,
    19e-5,
    5e-5,
    2e-5,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0
  ];
  var CMF_1931 = (() => {
    const out = [];
    for (let i = 0; i < 36; i++) {
      out.push([X_BAR_1931[i], Y_BAR_1931[i], Z_BAR_1931[i]]);
    }
    return out;
  })();

  // lib/dist/spectral/illuminants.js
  var D652 = [
    49.9755,
    54.6482,
    82.7549,
    91.486,
    93.4318,
    86.6823,
    104.865,
    117.008,
    117.812,
    114.861,
    115.923,
    108.811,
    109.354,
    107.802,
    104.79,
    107.689,
    104.405,
    104.046,
    100,
    96.3342,
    95.788,
    88.6856,
    90.0062,
    89.5991,
    87.6987,
    83.2886,
    83.6992,
    80.0268,
    80.2146,
    82.2778,
    78.2842,
    69.7213,
    71.6091,
    74.349,
    61.604,
    69.8856
  ];
  var D502 = [
    24.488,
    27.1791,
    39.5808,
    44.9117,
    46.6383,
    47.1834,
    60.0322,
    67.3963,
    68.6125,
    67.3534,
    70.2992,
    67.9145,
    70.6403,
    71.826,
    73.2832,
    78.4108,
    78.8729,
    80.9152,
    80.4498,
    81.5301,
    84.5717,
    80.7019,
    86.1606,
    88.7676,
    89.909,
    87.8907,
    91.7404,
    90.715,
    92.5969,
    96.6097,
    92.1183,
    83.407,
    86.1611,
    90.7204,
    75.0727,
    86.1635
  ];
  var A3 = [
    9.7951,
    12.0853,
    14.708,
    17.6753,
    20.995,
    24.6709,
    28.7027,
    33.0859,
    37.8121,
    42.8693,
    48.2423,
    53.9132,
    59.8611,
    66.0635,
    72.4959,
    79.1326,
    85.947,
    92.912,
    100,
    107.184,
    114.436,
    121.731,
    129.043,
    136.346,
    143.618,
    150.836,
    157.979,
    165.028,
    171.963,
    178.769,
    185.429,
    191.931,
    198.261,
    204.409,
    210.365,
    216.117
  ];
  var F22 = [
    1.18,
    1.48,
    1.84,
    2.15,
    3.44,
    15.69,
    3.85,
    3.74,
    4.19,
    4.62,
    5.06,
    34.98,
    11.81,
    6.27,
    7.32,
    8.45,
    9.92,
    11.51,
    12.79,
    13.71,
    14.2,
    14.06,
    13.18,
    11.92,
    10.51,
    9.05,
    7.65,
    6.27,
    5.16,
    4.1,
    3.2,
    2.43,
    1.89,
    1.46,
    1.1,
    0.81
  ];
  var E = new Array(36).fill(100);
  var WAVELENGTHS_NM = (() => {
    const out = [];
    for (let i = 0; i < 36; i++)
      out.push(380 + i * 10);
    return out;
  })();

  // lib/dist/spectral/spd.js
  function reflectiveToXYZ(reflectance, illuminant = D652) {
    let X = 0, Y = 0, Z = 0;
    let Yn2 = 0;
    for (let i = 0; i < 36; i++) {
      const E3 = illuminant[i];
      X += reflectance[i] * E3 * CMF_1931[i][0];
      Y += reflectance[i] * E3 * CMF_1931[i][1];
      Z += reflectance[i] * E3 * CMF_1931[i][2];
      Yn2 += E3 * CMF_1931[i][1];
    }
    return xyz(X / Yn2, Y / Yn2, Z / Yn2);
  }
  var D65_Y = (() => {
    let Y = 0;
    for (let i = 0; i < 36; i++)
      Y += D652[i] * CMF_1931[i][1];
    return Y;
  })();

  // lib/js/components/pigment-mixer.js
  function gauss(center, width, height) {
    return WAVELENGTHS_NM.map((nm) => {
      const t = (nm - center) / width;
      return Math.max(5e-3, Math.min(1, height * Math.exp(-t * t)));
    });
  }
  function sigmoid(edge, width, low, high) {
    return WAVELENGTHS_NM.map((nm) => {
      const t = (nm - edge) / width;
      return Math.max(5e-3, Math.min(1, low + (high - low) / (1 + Math.exp(-t))));
    });
  }
  function flat(v) {
    return new Array(36).fill(v);
  }
  var PIGMENTS = {
    white: { name: "Titanium white", spectrum: flat(0.95) },
    black: { name: "Mars black", spectrum: flat(0.04) },
    ultramarine: { name: "Ultramarine blue", spectrum: gauss(440, 50, 0.62).map((v, i) => v + (WAVELENGTHS_NM[i] > 640 ? 0.1 : 0)) },
    cobaltblue: { name: "Cobalt blue", spectrum: gauss(460, 65, 0.55) },
    cadyellow: { name: "Cadmium yellow", spectrum: sigmoid(520, 12, 0.04, 0.85) },
    cadred: { name: "Cadmium red", spectrum: sigmoid(595, 15, 0.04, 0.78) },
    alizarin: { name: "Alizarin crimson", spectrum: sigmoid(605, 18, 0.03, 0.6).map((v, i) => WAVELENGTHS_NM[i] < 460 ? Math.max(v, 0.1) : v) },
    viridian: { name: "Viridian green", spectrum: gauss(520, 35, 0.55) },
    yellowochre: { name: "Yellow ochre", spectrum: sigmoid(530, 22, 0.1, 0.6) },
    burntsienna: { name: "Burnt sienna", spectrum: sigmoid(575, 25, 0.05, 0.5) }
  };
  function spectrumToHex(spectrum) {
    const xyz2 = reflectiveToXYZ(spectrum, D652);
    const lin = fromXYZ5(xyz2);
    const cs = [
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ];
    return toHex(encode(cs));
  }
  function naiveRgbMix(hexA, hexB, ratio) {
    function fromHex3(h) {
      return [
        parseInt(h.slice(1, 3), 16) / 255,
        parseInt(h.slice(3, 5), 16) / 255,
        parseInt(h.slice(5, 7), 16) / 255
      ];
    }
    const a = fromHex3(hexA), b = fromHex3(hexB);
    const linA = decode(a);
    const linB = decode(b);
    const mix2 = [
      linA[0] * ratio + linB[0] * (1 - ratio),
      linA[1] * ratio + linB[1] * (1 - ratio),
      linA[2] * ratio + linB[2] * (1 - ratio)
    ];
    return toHex(encode(mix2));
  }
  var PigmentMixer = class extends HTMLElement {
    static get observedAttributes() {
      return ["pigment-a", "pigment-b", "ratio"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._root) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="pigment-host"></div>`;
      this._root = this.querySelector(".pigment-host");
    }
    render() {
      const pa = this.getAttribute("pigment-a") || "ultramarine";
      const pb = this.getAttribute("pigment-b") || "cadyellow";
      const ratio = Math.max(0, Math.min(1, parseFloat(this.getAttribute("ratio") ?? "0.5")));
      const A5 = PIGMENTS[pa] || PIGMENTS.ultramarine;
      const B4 = PIGMENTS[pb] || PIGMENTS.cadyellow;
      const hexA = spectrumToHex(A5.spectrum);
      const hexB = spectrumToHex(B4.spectrum);
      const mixedSpectrum = mix(A5.spectrum, B4.spectrum, ratio);
      const hexKM = spectrumToHex(mixedSpectrum);
      const hexRGB = naiveRgbMix(hexA, hexB, ratio);
      this._root.innerHTML = `
      <div class="pigment-row pigment-row--inputs">
        <div class="pigment-cell">
          <div class="pigment-swatch" style="background:${hexA}"></div>
          <div class="pigment-meta"><strong>${A5.name}</strong><br><span>${(ratio * 100).toFixed(0)}%</span></div>
        </div>
        <div class="pigment-cell">
          <div class="pigment-swatch" style="background:${hexB}"></div>
          <div class="pigment-meta"><strong>${B4.name}</strong><br><span>${((1 - ratio) * 100).toFixed(0)}%</span></div>
        </div>
      </div>
      <div class="pigment-row pigment-row--outputs">
        <div class="pigment-cell pigment-cell--km">
          <div class="pigment-swatch" style="background:${hexKM}"></div>
          <div class="pigment-meta"><strong>Kubelka-Munk mix</strong><br><span>physical pigment blend \xB7 ${hexKM}</span></div>
        </div>
        <div class="pigment-cell pigment-cell--rgb">
          <div class="pigment-swatch" style="background:${hexRGB}"></div>
          <div class="pigment-meta"><strong>RGB midpoint</strong><br><span>naive sRGB average \xB7 ${hexRGB}</span></div>
        </div>
      </div>
    `;
      this._renderSpectrumChart(A5.spectrum, B4.spectrum, mixedSpectrum, hexA, hexB, hexKM);
    }
    _renderSpectrumChart(specA, specB, specMix, hexA, hexB, hexMix) {
      let chartCanvas = this._root.querySelector(".pigment-chart");
      if (!chartCanvas) {
        this._root.insertAdjacentHTML("beforeend", '<canvas class="pigment-chart"></canvas>');
        chartCanvas = this._root.querySelector(".pigment-chart");
      }
      const wCss = Math.min(this.offsetWidth || 700, 700);
      const hCss = 220;
      const { ctx, w, h } = setupCanvas(chartCanvas, wCss, hCss);
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--bg-card").trim() || "#fff";
      ctx.fillRect(0, 0, w, h);
      const padL = 30, padR = 8, padT = 12, padB = 22;
      const cw = w - padL - padR;
      const ch = h - padT - padB;
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--border").trim() || "#ccc";
      ctx.lineWidth = 1;
      ctx.font = "10px ui-monospace, monospace";
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      [400, 500, 600, 700].forEach((nm) => {
        const x = padL + (nm - 380) / (730 - 380) * cw;
        ctx.beginPath();
        ctx.moveTo(x, padT);
        ctx.lineTo(x, padT + ch);
        ctx.stroke();
        ctx.fillText(String(nm), x - 10, padT + ch + 14);
      });
      [0, 0.5, 1].forEach((r) => {
        const y = padT + ch - r * ch;
        ctx.beginPath();
        ctx.moveTo(padL, y);
        ctx.lineTo(padL + cw, y);
        ctx.stroke();
        ctx.fillText(r.toFixed(1), 2, y + 4);
      });
      function plot(spec, color) {
        ctx.beginPath();
        WAVELENGTHS_NM.forEach((nm, i) => {
          const x = padL + (nm - 380) / (730 - 380) * cw;
          const y = padT + ch - spec[i] * ch;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.stroke();
      }
      plot(specA, hexA);
      plot(specB, hexB);
      plot(specMix, hexMix);
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      ctx.font = "10px ui-monospace, monospace";
      ctx.fillText("reflectance vs \u03BB (nm)", padL + 4, padT + 12);
    }
    static get PIGMENTS() {
      return PIGMENTS;
    }
  };
  customElements.define("pigment-mixer", PigmentMixer);

  // lib/js/components/adaptation-viewer.js
  var WHITES = { D65, D50, A: A2, F2 };
  var LABELS = {
    D65: "D65 (daylight ~6500K)",
    D50: "D50 (warm daylight ~5000K)",
    A: "A (tungsten ~2856K)",
    F2: "F2 (cool white fluorescent)"
  };
  var AdaptationViewer = class extends HTMLElement {
    static get observedAttributes() {
      return ["src-white", "dst-white", "mode"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._canvas && this._sourceData) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="adapt-host">
      <canvas></canvas>
      <p class="adapt-empty" style="color:var(--text-muted);font-size:var(--text-sm);">Drop or pick an image to start.</p>
    </div>`;
      this._canvas = this.querySelector("canvas");
      this._empty = this.querySelector(".adapt-empty");
    }
    setImage(image) {
      const work = document.createElement("canvas");
      work.width = image.naturalWidth || image.width;
      work.height = image.naturalHeight || image.height;
      work.getContext("2d").drawImage(image, 0, 0);
      this._sourceData = work.getContext("2d").getImageData(0, 0, work.width, work.height);
      this._sourceWidth = work.width;
      this._sourceHeight = work.height;
      if (this._empty) this._empty.style.display = "none";
      this.render();
    }
    render() {
      if (!this._canvas || !this._sourceData) return;
      const srcKey = this.getAttribute("src-white") || "D65";
      const dstKey = this.getAttribute("dst-white") || "A";
      const mode = this.getAttribute("mode") || "split";
      const srcW = WHITES[srcKey] || D65;
      const dstW = WHITES[dstKey] || A2;
      const M3 = bradfordMatrix(srcW, dstW);
      const sW = this._sourceWidth, sH = this._sourceHeight;
      const src = this._sourceData.data;
      const adapted = new ImageData(sW, sH);
      const dst = adapted.data;
      for (let i = 0; i < src.length; i += 4) {
        const r = src[i] / 255, g = src[i + 1] / 255, b = src[i + 2] / 255;
        const lin = decode([r, g, b]);
        const xyz2 = toXYZ5(lin);
        const adaptedXyz = mulMat3Vec3(M3, xyz2);
        const linOut = fromXYZ5(adaptedXyz);
        const cs = [
          Math.max(0, Math.min(1, linOut[0])),
          Math.max(0, Math.min(1, linOut[1])),
          Math.max(0, Math.min(1, linOut[2]))
        ];
        const enc = encode(cs);
        dst[i] = Math.round(enc[0] * 255);
        dst[i + 1] = Math.round(enc[1] * 255);
        dst[i + 2] = Math.round(enc[2] * 255);
        dst[i + 3] = src[i + 3];
      }
      const targetW = Math.min(900, this.offsetWidth || 900);
      const aspect = sH / sW;
      let canvW, canvH, drawW;
      if (mode === "split") {
        drawW = targetW / 2;
        canvW = targetW;
        canvH = drawW * aspect;
      } else {
        drawW = targetW;
        canvW = targetW;
        canvH = canvW * aspect;
      }
      const { ctx, w, h } = setupCanvas(this._canvas, canvW, canvH);
      const origCv = document.createElement("canvas");
      origCv.width = sW;
      origCv.height = sH;
      origCv.getContext("2d").putImageData(this._sourceData, 0, 0);
      const adaptCv = document.createElement("canvas");
      adaptCv.width = sW;
      adaptCv.height = sH;
      adaptCv.getContext("2d").putImageData(adapted, 0, 0);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      if (mode === "split") {
        ctx.drawImage(origCv, 0, 0, drawW, h);
        ctx.drawImage(adaptCv, drawW, 0, drawW, h);
        ctx.strokeStyle = "rgba(255,255,255,0.6)";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(drawW, 0);
        ctx.lineTo(drawW, h);
        ctx.stroke();
        ctx.fillStyle = "rgba(0,0,0,0.65)";
        ctx.fillRect(4, 4, 200, 20);
        ctx.fillRect(drawW + 4, 4, 240, 20);
        ctx.fillStyle = "#fff";
        ctx.font = "11px ui-monospace, monospace";
        ctx.fillText("source \xB7 " + LABELS[srcKey], 8, 19);
        ctx.fillText("adapted \xB7 " + LABELS[dstKey], drawW + 8, 19);
      } else {
        ctx.drawImage(adaptCv, 0, 0, w, h);
      }
    }
  };
  customElements.define("adaptation-viewer", AdaptationViewer);

  // lib/dist/tonemap/reinhard.js
  function reinhardSimple(x) {
    return x / (1 + x);
  }
  function reinhardExtended(x, whitePoint = 4) {
    const W2 = whitePoint * whitePoint;
    return x * (1 + x / W2) / (1 + x);
  }
  function applySimple(rgb) {
    return linearSRGB(reinhardSimple(rgb[0]), reinhardSimple(rgb[1]), reinhardSimple(rgb[2]));
  }
  function applyExtended(rgb, whitePoint = 4) {
    return linearSRGB(reinhardExtended(rgb[0], whitePoint), reinhardExtended(rgb[1], whitePoint), reinhardExtended(rgb[2], whitePoint));
  }
  var Y_WEIGHTS = [0.2126390059, 0.7151686788, 0.0721923154];
  function luminance(rgb) {
    return Y_WEIGHTS[0] * rgb[0] + Y_WEIGHTS[1] * rgb[1] + Y_WEIGHTS[2] * rgb[2];
  }
  function applyLuminancePreserving(rgb, whitePoint = 4) {
    const Y = luminance(rgb);
    if (Y <= 0)
      return rgb;
    const Y_new = reinhardExtended(Y, whitePoint);
    const gain = Y_new / Y;
    return linearSRGB(rgb[0] * gain, rgb[1] * gain, rgb[2] * gain);
  }

  // lib/dist/tonemap/aces.js
  var A4 = 2.51;
  var B3 = 0.03;
  var C4 = 2.43;
  var D = 0.59;
  var E2 = 0.14;
  function acesNarkowicz(x) {
    return x * (A4 * x + B3) / (x * (C4 * x + D) + E2);
  }
  function applyACES(rgb) {
    return linearSRGB(acesNarkowicz(rgb[0]), acesNarkowicz(rgb[1]), acesNarkowicz(rgb[2]));
  }

  // lib/js/components/tonemap-strip.js
  var OPS = [
    {
      id: "clip",
      label: "naive clip",
      note: "min(x, 1) per channel",
      apply: function(rgb) {
        return [Math.min(1, rgb[0]), Math.min(1, rgb[1]), Math.min(1, rgb[2])];
      }
    },
    {
      id: "reinSimple",
      label: "Reinhard simple",
      note: "x/(1+x); asymptotic, never reaches 1",
      apply: function(rgb) {
        return applySimple(rgb);
      }
    },
    {
      id: "reinExt",
      label: "Reinhard extended (W=whitePt)",
      note: "maps whitePoint exactly to 1.0",
      apply: function(rgb, wp) {
        return applyExtended(rgb, wp);
      }
    },
    {
      id: "reinLum",
      label: "Reinhard luminance-preserving",
      note: "compress Y only; keep RGB ratios",
      apply: function(rgb, wp) {
        return applyLuminancePreserving(rgb, wp);
      }
    },
    {
      id: "aces",
      label: "ACES (Narkowicz fit)",
      note: "filmic toe + highlight roll-off",
      apply: function(rgb) {
        return applyACES(rgb);
      }
    }
  ];
  var TonemapStrip = class extends HTMLElement {
    static get observedAttributes() {
      return ["exposure", "white-point", "max-stop"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._root) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="tonemap-host"></div>`;
      this._root = this.querySelector(".tonemap-host");
    }
    render() {
      const exposure = parseFloat(this.getAttribute("exposure") ?? "1");
      const whitePoint = parseFloat(this.getAttribute("white-point") ?? "4");
      const maxStop = parseFloat(this.getAttribute("max-stop") ?? "8");
      this._root.innerHTML = OPS.map((op) => `
      <div class="tonemap-row">
        <div class="tonemap-label">
          <strong>${op.label}</strong>
          <div class="tonemap-note">${op.note}</div>
        </div>
        <canvas data-op="${op.id}" class="tonemap-canvas"></canvas>
      </div>
    `).join("");
      const canvases = this._root.querySelectorAll("canvas[data-op]");
      canvases.forEach((canv) => {
        const op = OPS.find((o) => o.id === canv.dataset.op);
        const wCss = Math.min(this.offsetWidth || 600, 720) - 200;
        const hCss = 48;
        const { ctx, w, h } = setupCanvas(canv, wCss, hCss);
        const imgData = ctx.createImageData(Math.round(w), Math.round(h));
        const data = imgData.data;
        const cols = Math.round(w);
        const rgbStrip = [];
        for (let i = 0; i < cols; i++) {
          const t = i / (cols - 1);
          const linVal = t * maxStop * exposure;
          rgbStrip.push([linVal, linVal, linVal]);
        }
        const mapped = rgbStrip.map((rgb) => op.apply(rgb, whitePoint));
        for (let py = 0; py < Math.round(h); py++) {
          for (let px = 0; px < cols; px++) {
            const m = mapped[px];
            const cs = [
              Math.max(0, Math.min(1, m[0])),
              Math.max(0, Math.min(1, m[1])),
              Math.max(0, Math.min(1, m[2]))
            ];
            const enc = encode(cs);
            const i = (py * cols + px) * 4;
            data[i] = Math.round(enc[0] * 255);
            data[i + 1] = Math.round(enc[1] * 255);
            data[i + 2] = Math.round(enc[2] * 255);
            data[i + 3] = 255;
          }
        }
        const tmp = document.createElement("canvas");
        tmp.width = cols;
        tmp.height = Math.round(h);
        tmp.getContext("2d").putImageData(imgData, 0, 0);
        ctx.imageSmoothingEnabled = true;
        ctx.drawImage(tmp, 0, 0, w, h);
      });
    }
  };
  customElements.define("tonemap-strip", TonemapStrip);

  // lib/js/components/dither-compare.js
  function oklabToHexBytes(lab) {
    const xyz2 = toXYZ(lab);
    const lin = fromXYZ5(xyz2);
    const cs = [
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ];
    const enc = encode(cs);
    return [
      Math.round(enc[0] * 255),
      Math.round(enc[1] * 255),
      Math.round(enc[2] * 255)
    ];
  }
  var DitherCompare = class extends HTMLElement {
    static get observedAttributes() {
      return ["k"];
    }
    connectedCallback() {
      this._mount();
    }
    attributeChangedCallback() {
      if (this._source) this.run();
    }
    _mount() {
      this.innerHTML = `<div class="dither-host">
      <div class="dither-grid">
        <div class="dither-cell">
          <h4>Palette (${this.getAttribute("k") || 8} colors)</h4>
          <div class="dither-palette" id="dp-palette"></div>
        </div>
        <div class="dither-cell">
          <h4>Nearest-neighbor (no dither)</h4>
          <canvas class="dither-canvas" id="dp-nn"></canvas>
        </div>
        <div class="dither-cell">
          <h4>Floyd-Steinberg (error-diffused)</h4>
          <canvas class="dither-canvas" id="dp-fs"></canvas>
        </div>
      </div>
      <p class="dither-status" style="color:var(--text-muted);font-size:var(--text-sm);">Drop an image to begin.</p>
    </div>`;
      this._paletteEl = this.querySelector("#dp-palette");
      this._nnCanvas = this.querySelector("#dp-nn");
      this._fsCanvas = this.querySelector("#dp-fs");
      this._status = this.querySelector(".dither-status");
    }
    setImage(image) {
      if (!this._paletteEl) this._mount();
      const scale = Math.min(1, 320 / Math.max(image.naturalWidth, image.naturalHeight));
      const W = Math.round(image.naturalWidth * scale);
      const H = Math.round(image.naturalHeight * scale);
      const work = document.createElement("canvas");
      work.width = W;
      work.height = H;
      work.getContext("2d").drawImage(image, 0, 0, W, H);
      this._source = work.getContext("2d").getImageData(0, 0, W, H);
      this._sourceWidth = W;
      this._sourceHeight = H;
      this.run();
    }
    run() {
      if (!this._source) return;
      const k = Math.max(2, Math.min(32, parseInt(this.getAttribute("k") || "8", 10)));
      const W = this._sourceWidth, H = this._sourceHeight;
      const data = this._source.data;
      this._status.textContent = "Quantizing\u2026";
      requestAnimationFrame(() => {
        const t = performance.now();
        const pixels = [];
        const grid = [];
        for (let y = 0; y < H; y++) {
          const row = [];
          for (let x = 0; x < W; x++) {
            const i = (y * W + x) * 4;
            const r = data[i] / 255, g = data[i + 1] / 255, b = data[i + 2] / 255;
            const lin = decode([r, g, b]);
            const xyz2 = toXYZ5(lin);
            const lab = fromXYZ(xyz2);
            pixels.push(lab);
            row.push(lab);
          }
          grid.push(row);
        }
        const { palette } = quantize(pixels, { k, seed: 42 });
        this._renderPalette(palette);
        this._renderQuantized(
          grid,
          palette,
          this._nnCanvas,
          /* dither */
          false
        );
        this._renderQuantized(
          grid,
          palette,
          this._fsCanvas,
          /* dither */
          true
        );
        const elapsed = (performance.now() - t).toFixed(0);
        this._status.textContent = `${k} colors, ${W}\xD7${H} samples \u2014 ${elapsed}ms total`;
      });
    }
    _renderPalette(palette) {
      const k = this.getAttribute("k") || 8;
      const swatches = palette.map((lab) => {
        const rgb = oklabToHexBytes(lab);
        const hex = "#" + rgb.map((v) => v.toString(16).padStart(2, "0")).join("");
        return `<div class="dither-swatch" style="background:${hex}" title="${hex}"></div>`;
      }).join("");
      this._paletteEl.innerHTML = swatches;
      this.querySelector("#dp-palette").previousElementSibling.textContent = `Palette (${palette.length} colors)`;
    }
    _renderQuantized(grid, palette, canvas, useDither) {
      const H = grid.length, W = grid[0].length;
      const wCss = Math.min(this.offsetWidth || 400, 480);
      const hCss = Math.round(wCss * H / W);
      const { ctx, w, h } = setupCanvas(canvas, wCss, hCss);
      let outIndices;
      if (useDither) {
        const { indices } = ditherFloydSteinberg(grid, palette);
        outIndices = indices;
      } else {
        outIndices = grid.map((row) => row.map((c) => {
          let best = 0, bestDist = Infinity;
          for (let i = 0; i < palette.length; i++) {
            const dL = c[0] - palette[i][0];
            const dA = c[1] - palette[i][1];
            const dB = c[2] - palette[i][2];
            const d = dL * dL + dA * dA + dB * dB;
            if (d < bestDist) {
              bestDist = d;
              best = i;
            }
          }
          return best;
        }));
      }
      const tmp = document.createElement("canvas");
      tmp.width = W;
      tmp.height = H;
      const imgData = tmp.getContext("2d").createImageData(W, H);
      const data = imgData.data;
      const paletteBytes = palette.map(oklabToHexBytes);
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const idx = outIndices[y][x];
          const rgb = paletteBytes[idx];
          const i = (y * W + x) * 4;
          data[i] = rgb[0];
          data[i + 1] = rgb[1];
          data[i + 2] = rgb[2];
          data[i + 3] = 255;
        }
      }
      tmp.getContext("2d").putImageData(imgData, 0, 0);
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(tmp, 0, 0, w, h);
    }
  };
  customElements.define("dither-compare", DitherCompare);

  // lib/js/components/spd-chart.js
  var ILLUMINANTS = {
    D65: { name: "D65 ~6500K", spd: D652, color: "oklch(0.554 0.180 264)", wpXYZ: [0.95046, 1, 1.08906] },
    D50: { name: "D50 ~5000K", spd: D502, color: "oklch(0.620 0.180 60)", wpXYZ: [0.9643, 1, 0.8251] },
    A: { name: "A 2856K (tungsten)", spd: A3, color: "oklch(0.700 0.180 50)", wpXYZ: [1.0985, 1, 0.35585] },
    F2: { name: "F2 cool white", spd: F22, color: "oklch(0.620 0.180 150)", wpXYZ: [0.99186, 1, 0.67393] },
    E: { name: "E equal energy", spd: E, color: "oklch(0.600 0.020 264)", wpXYZ: [1, 1, 1] }
  };
  function gauss2(center, width, height) {
    return WAVELENGTHS_NM.map((nm) => {
      const t = (nm - center) / width;
      return Math.max(0.04, Math.min(1, height * Math.exp(-t * t)));
    });
  }
  function sigmoid2(edge, width, lo, hi) {
    return WAVELENGTHS_NM.map((nm) => {
      const t = (nm - edge) / width;
      return Math.max(0.04, Math.min(1, lo + (hi - lo) / (1 + Math.exp(-t))));
    });
  }
  var SAMPLES = [
    { name: "white", spectrum: new Array(36).fill(0.85) },
    { name: "red", spectrum: sigmoid2(595, 15, 0.05, 0.78) },
    { name: "green", spectrum: gauss2(520, 35, 0.55) },
    { name: "blue", spectrum: gauss2(450, 50, 0.55) },
    { name: "orange", spectrum: sigmoid2(550, 18, 0.05, 0.72) },
    { name: "magenta", spectrum: WAVELENGTHS_NM.map((nm) => {
      const t1 = (nm - 430) / 40;
      const t2 = (nm - 660) / 40;
      return Math.max(0.04, Math.min(1, 0.6 * (Math.exp(-(t1 * t1)) + Math.exp(-(t2 * t2)))));
    }) },
    { name: "skin", spectrum: sigmoid2(540, 30, 0.2, 0.55) },
    { name: "gray", spectrum: new Array(36).fill(0.18) }
  ];
  function spectrumToHex2(spectrum, illuminant) {
    const sceneXyz = reflectiveToXYZ(spectrum, illuminant.spd);
    const adaptM = bradfordMatrix(illuminant.wpXYZ, D65);
    const adaptedXyz = mulMat3Vec3(adaptM, sceneXyz);
    const lin = fromXYZ5(sceneXyz);
    const cs = [
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ];
    const enc = encode(cs);
    return "#" + [enc[0], enc[1], enc[2]].map((v) => Math.round(v * 255).toString(16).padStart(2, "0")).join("");
  }
  var SPDChart = class extends HTMLElement {
    static get observedAttributes() {
      return ["show"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._root) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="spd-host">
      <canvas class="spd-chart-canvas"></canvas>
      <div class="spd-samples"></div>
    </div>`;
      this._root = this.querySelector(".spd-host");
      this._chart = this.querySelector(".spd-chart-canvas");
      this._samples = this.querySelector(".spd-samples");
    }
    render() {
      const showAttr = this.getAttribute("show") || "D65,A,D50,F2";
      const showList = showAttr.split(",").map((s) => s.trim()).filter((k) => ILLUMINANTS[k]);
      this._renderChart(showList);
      this._renderSamples(showList);
    }
    _renderChart(showList) {
      const wCss = Math.min(this.offsetWidth || 760, 760);
      const hCss = 280;
      const { ctx, w, h } = setupCanvas(this._chart, wCss, hCss);
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--bg-card").trim() || "#fff";
      ctx.fillRect(0, 0, w, h);
      const padL = 36, padR = 8, padT = 16, padB = 28;
      const cw = w - padL - padR;
      const ch = h - padT - padB;
      let maxY = 0;
      for (const key of showList) maxY = Math.max(maxY, ...ILLUMINANTS[key].spd);
      maxY = Math.ceil(maxY / 25) * 25;
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--border").trim() || "#ccc";
      ctx.lineWidth = 1;
      ctx.font = "10px ui-monospace, monospace";
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      [400, 500, 600, 700].forEach((nm) => {
        const x = padL + (nm - 380) / (730 - 380) * cw;
        ctx.beginPath();
        ctx.moveTo(x, padT);
        ctx.lineTo(x, padT + ch);
        ctx.stroke();
        ctx.fillText(String(nm), x - 10, padT + ch + 18);
      });
      for (let v = 0; v <= maxY; v += maxY / 4) {
        const y = padT + ch - v / maxY * ch;
        ctx.beginPath();
        ctx.moveTo(padL, y);
        ctx.lineTo(padL + cw, y);
        ctx.stroke();
        ctx.fillText(v.toFixed(0), 4, y + 4);
      }
      for (const key of showList) {
        const { spd, color } = ILLUMINANTS[key];
        ctx.beginPath();
        WAVELENGTHS_NM.forEach((nm, i) => {
          const x = padL + (nm - 380) / (730 - 380) * cw;
          const y = padT + ch - spd[i] / maxY * ch;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.stroke();
      }
      ctx.font = "11px ui-monospace, monospace";
      let lx = padL + 8;
      for (const key of showList) {
        const { name, color } = ILLUMINANTS[key];
        ctx.fillStyle = color;
        ctx.fillRect(lx, padT + 4, 12, 8);
        ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text").trim() || "#111";
        ctx.fillText(name, lx + 16, padT + 12);
        lx += ctx.measureText(name).width + 36;
      }
    }
    _renderSamples(showList) {
      let html = '<table class="spd-table"><thead><tr><th></th>';
      for (const key of showList) {
        html += "<th>" + ILLUMINANTS[key].name + "</th>";
      }
      html += "</tr></thead><tbody>";
      for (const sample of SAMPLES) {
        html += "<tr><th>" + sample.name + "</th>";
        for (const key of showList) {
          const hex = spectrumToHex2(sample.spectrum, ILLUMINANTS[key]);
          html += '<td><div class="spd-swatch" style="background:' + hex + '"></div></td>';
        }
        html += "</tr>";
      }
      html += "</tbody></table>";
      this._samples.innerHTML = html;
    }
  };
  customElements.define("spd-chart", SPDChart);

  // lib/js/components/procedural-palette.js
  function clip01(v) {
    return Math.max(0, Math.min(1, v));
  }
  function clipLin(rgb) {
    return [clip01(rgb[0]), clip01(rgb[1]), clip01(rgb[2])];
  }
  function linToHex(lin) {
    return toHex(encode(clipLin(lin)));
  }
  function iqColor(t, a, b, c, d) {
    return [0, 1, 2].map((i) => a[i] + b[i] * Math.cos(2 * Math.PI * (c[i] * t + d[i])));
  }
  var ProceduralPalette = class extends HTMLElement {
    static get observedAttributes() {
      return ["algorithm", "params"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._root) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="proc-host">
      <canvas class="proc-ramp"></canvas>
      <div class="proc-strip"></div>
      <canvas class="proc-y"></canvas>
    </div>`;
      this._root = this.querySelector(".proc-host");
      this._ramp = this.querySelector(".proc-ramp");
      this._strip = this.querySelector(".proc-strip");
      this._yChart = this.querySelector(".proc-y");
    }
    set params(p) {
      this._params = p;
      this.render();
    }
    set iqParams(p) {
      this._iqParams = p;
      this.render();
    }
    render() {
      const algo = this.getAttribute("algorithm") || "cubehelix";
      const N_RAMP = 256;
      const N_STRIP = 9;
      function sampler(t) {
        if (algo === "iq") {
          const p2 = this._iqParams || { a: [0.5, 0.5, 0.5], b: [0.5, 0.5, 0.5], c: [1, 1, 1], d: [0, 0.33, 0.67] };
          return iqColor(t, p2.a, p2.b, p2.c, p2.d);
        }
        const p = this._params || { start: 0.5, rotations: -1.5, hue: 1, gamma: 1 };
        return cubehelix(t, p);
      }
      sampler = sampler.bind(this);
      const wCss = Math.min(this.offsetWidth || 720, 720);
      const hCss = 64;
      const { ctx, w, h } = setupCanvas(this._ramp, wCss, hCss);
      const tmp = document.createElement("canvas");
      tmp.width = N_RAMP;
      tmp.height = 1;
      const imgData = tmp.getContext("2d").createImageData(N_RAMP, 1);
      for (let i = 0; i < N_RAMP; i++) {
        const t = i / (N_RAMP - 1);
        const lin = sampler(t);
        const enc = encode(clipLin(lin));
        imgData.data[i * 4] = Math.round(enc[0] * 255);
        imgData.data[i * 4 + 1] = Math.round(enc[1] * 255);
        imgData.data[i * 4 + 2] = Math.round(enc[2] * 255);
        imgData.data[i * 4 + 3] = 255;
      }
      tmp.getContext("2d").putImageData(imgData, 0, 0);
      ctx.imageSmoothingEnabled = true;
      ctx.drawImage(tmp, 0, 0, w, h);
      const hexes = [];
      for (let i = 0; i < N_STRIP; i++) {
        const t = i / (N_STRIP - 1);
        hexes.push(linToHex(sampler(t)));
      }
      this._strip.innerHTML = hexes.map((hex) => `
      <div class="proc-swatch" style="background:${hex}">
        <span>${hex}</span>
      </div>
    `).join("");
      const wY = Math.min(this.offsetWidth || 720, 720);
      const hY = 120;
      const { ctx: yctx, w: yw, h: yh } = setupCanvas(this._yChart, wY, hY);
      yctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--bg-card").trim() || "#fff";
      yctx.fillRect(0, 0, yw, yh);
      const padL = 28, padR = 8, padT = 12, padB = 20;
      const cw = yw - padL - padR;
      const ch = yh - padT - padB;
      yctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--border").trim() || "#ccc";
      yctx.lineWidth = 1;
      yctx.font = "10px ui-monospace, monospace";
      yctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      [0, 0.5, 1].forEach((v) => {
        const y = padT + ch - v * ch;
        yctx.beginPath();
        yctx.moveTo(padL, y);
        yctx.lineTo(padL + cw, y);
        yctx.stroke();
        yctx.fillText(v.toFixed(1), 4, y + 4);
      });
      yctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim() || "oklch(0.55 0.18 264)";
      yctx.lineWidth = 2;
      yctx.beginPath();
      for (let i = 0; i < N_RAMP; i++) {
        const t = i / (N_RAMP - 1);
        const lin = clipLin(sampler(t));
        const Y = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
        const x = padL + i / (N_RAMP - 1) * cw;
        const y = padT + ch - Y * ch;
        if (i === 0) yctx.moveTo(x, y);
        else yctx.lineTo(x, y);
      }
      yctx.stroke();
      yctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      yctx.fillText("relative luminance Y vs t", padL + 4, padT + 12);
    }
  };
  customElements.define("procedural-palette", ProceduralPalette);

  // lib/js/components/tonal-palette.js
  var TONES = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100];
  function hctToHexInGamut(H, C5, T) {
    let lo = 0, hi = C5;
    const inGamut2 = (c) => {
      const xyz3 = toXYZ11([H, c, T]);
      const lin2 = fromXYZ5(xyz3);
      return lin2[0] >= -5e-3 && lin2[0] <= 1.005 && lin2[1] >= -5e-3 && lin2[1] <= 1.005 && lin2[2] >= -5e-3 && lin2[2] <= 1.005;
    };
    if (inGamut2(C5)) {
      lo = C5;
    } else {
      for (let i = 0; i < 18; i++) {
        const m = (lo + hi) / 2;
        if (inGamut2(m)) lo = m;
        else hi = m;
      }
    }
    const xyz2 = toXYZ11([H, lo, T]);
    const lin = fromXYZ5(xyz2);
    const clamped = [
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ];
    return toHex(encode(clamped));
  }
  function hexToHCT(hex) {
    const r = parseInt(hex.slice(1, 3), 16) / 255;
    const g = parseInt(hex.slice(3, 5), 16) / 255;
    const b = parseInt(hex.slice(5, 7), 16) / 255;
    const lin = decode([r, g, b]);
    const xyz2 = toXYZ5(lin);
    return fromXYZ11(xyz2);
  }
  var TonalPalette = class extends HTMLElement {
    static get observedAttributes() {
      return ["source"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._root) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="tonal-host"></div>`;
      this._root = this.querySelector(".tonal-host");
    }
    render() {
      const source = this.getAttribute("source") || "#3b82f6";
      if (!/^#[0-9a-fA-F]{6}$/.test(source)) return;
      const [H, C5, T] = hexToHCT(source);
      const palettes = [
        { name: "Primary", H, C: C5 },
        { name: "Secondary", H, C: Math.max(8, C5 * 0.33) },
        { name: "Tertiary", H: (H + 60) % 360, C: Math.max(8, C5 * 0.5) },
        { name: "Neutral", H, C: 4 },
        { name: "Neutral variant", H, C: 8 }
      ];
      let html = '<table class="tonal-table"><thead><tr><th></th>';
      for (const t of TONES) html += "<th>" + t + "</th>";
      html += "</tr></thead><tbody>";
      for (const p of palettes) {
        html += "<tr><th>" + p.name + "</th>";
        for (const t of TONES) {
          const hex = hctToHexInGamut(p.H, p.C, t);
          const textColor = t >= 50 ? "#111" : "#fff";
          html += '<td style="background:' + hex + ";color:" + textColor + '"><span>' + hex + "</span></td>";
        }
        html += "</tr>";
      }
      html += "</tbody></table>";
      html += '<div class="tonal-source">';
      html += "<strong>Source</strong> " + source + " \u2192 HCT(";
      html += "H=" + fmt(H, 1) + ", C=" + fmt(C5, 2) + ", T=" + fmt(T, 2) + ")";
      html += "</div>";
      this._root.innerHTML = html;
    }
  };
  customElements.define("tonal-palette", TonalPalette);

  // lib/js/components/kelvin-picker.js
  function plankianXY(T) {
    let x;
    if (T < 4e3) {
      x = -266123900 / (T * T * T) - 234358.9 / (T * T) + 877.6956 / T + 0.17991;
    } else {
      x = -3025846900 / (T * T * T) + 21070379e-1 / (T * T) + 222.6347 / T + 0.24039;
    }
    let y;
    if (T < 2222) {
      y = -1.1063814 * x * x * x - 1.3481102 * x * x + 2.18555832 * x - 0.20219683;
    } else if (T < 4e3) {
      y = -0.9549476 * x * x * x - 1.37418593 * x * x + 2.09137015 * x - 0.16748867;
    } else {
      y = 3.081758 * x * x * x - 5.8733867 * x * x + 3.75112997 * x - 0.37001483;
    }
    return [x, y];
  }
  function kelvinToHex(T) {
    const [x, y] = plankianXY(T);
    if (y === 0) return "#000000";
    const xyz2 = toXYZ14([x, y, 1]);
    const lin = fromXYZ5(xyz2);
    const m = Math.max(lin[0], lin[1], lin[2], 1e-6);
    const norm = [lin[0] / m, lin[1] / m, lin[2] / m];
    const clamped = norm.map((v) => Math.max(0, Math.min(1, v)));
    return toHex(encode(clamped));
  }
  var REFERENCE_ILLUMINANTS = [
    { name: "A", T: 2856, x: 0.4476, y: 0.4074 },
    { name: "D50", T: 5003, x: 0.3457, y: 0.3585 },
    { name: "D55", T: 5503, x: 0.3324, y: 0.3474 },
    { name: "D65", T: 6504, x: 0.3127, y: 0.329 },
    { name: "D75", T: 7504, x: 0.299, y: 0.3149 }
  ];
  var KelvinPicker = class extends HTMLElement {
    static get observedAttributes() {
      return ["temp"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._root) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="kelvin-host">
      <div class="kelvin-swatch"></div>
      <div class="kelvin-readout"></div>
      <canvas class="kelvin-locus"></canvas>
    </div>`;
      this._root = this.querySelector(".kelvin-host");
      this._sw = this.querySelector(".kelvin-swatch");
      this._readout = this.querySelector(".kelvin-readout");
      this._canvas = this.querySelector(".kelvin-locus");
    }
    render() {
      const T = Math.max(1500, Math.min(25e3, parseFloat(this.getAttribute("temp") ?? "6500")));
      const [x, y] = plankianXY(T);
      const hex = kelvinToHex(T);
      this._sw.style.background = hex;
      this._readout.innerHTML = "<div><strong>" + T.toFixed(0) + " K</strong></div><div>x = " + x.toFixed(4) + "</div><div>y = " + y.toFixed(4) + "</div><div>" + hex + "</div>";
      const rect = this._canvas.getBoundingClientRect();
      const cssW = rect.width > 10 ? rect.width : 360;
      const cssH = rect.height > 10 ? rect.height : Math.round(cssW * 7 / 8);
      const dpr = window.devicePixelRatio || 1;
      this._canvas.width = Math.round(cssW * dpr);
      this._canvas.height = Math.round(cssH * dpr);
      const ctx = this._canvas.getContext("2d");
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const w = cssW, h = cssH;
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--bg-card").trim() || "#fff";
      ctx.fillRect(0, 0, w, h);
      const xMin = 0.22, xMax = 0.62;
      const yMin = 0.2, yMax = 0.5;
      const X = (xv) => (xv - xMin) / (xMax - xMin) * w;
      const Y = (yv) => h - (yv - yMin) / (yMax - yMin) * h;
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--border").trim() || "#ccc";
      ctx.lineWidth = 1;
      ctx.font = "10px ui-monospace, monospace";
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      [0.3, 0.4, 0.5, 0.6].forEach((v) => {
        const px = X(v);
        ctx.beginPath();
        ctx.moveTo(px, 0);
        ctx.lineTo(px, h);
        ctx.stroke();
        ctx.fillText(v.toFixed(1), px + 2, h - 4);
      });
      [0.2, 0.3, 0.4, 0.5].forEach((v) => {
        const py = Y(v);
        ctx.beginPath();
        ctx.moveTo(0, py);
        ctx.lineTo(w, py);
        ctx.stroke();
        ctx.fillText(v.toFixed(1), 2, py - 2);
      });
      ctx.beginPath();
      let first = true;
      for (let t = 1500; t <= 25e3; t += t < 4e3 ? 100 : 500) {
        const [px, py] = plankianXY(t);
        if (px < xMin || px > xMax || py < yMin || py > yMax) continue;
        const cx2 = X(px), cy2 = Y(py);
        if (first) {
          ctx.moveTo(cx2, cy2);
          first = false;
        } else ctx.lineTo(cx2, cy2);
      }
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim() || "oklch(0.55 0.18 264)";
      ctx.lineWidth = 2;
      ctx.stroke();
      for (const ill of REFERENCE_ILLUMINANTS) {
        const cx2 = X(ill.x), cy2 = Y(ill.y);
        ctx.beginPath();
        ctx.arc(cx2, cy2, 3, 0, Math.PI * 2);
        ctx.fillStyle = "#fff";
        ctx.fill();
        ctx.strokeStyle = "#000";
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
        ctx.fillText(ill.name, cx2 + 5, cy2 - 4);
      }
      const cx = X(x), cy = Y(y);
      ctx.beginPath();
      ctx.arc(cx, cy, 7, 0, Math.PI * 2);
      ctx.fillStyle = hex;
      ctx.fill();
      ctx.strokeStyle = "#000";
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 1;
      ctx.stroke();
    }
  };
  customElements.define("kelvin-picker", KelvinPicker);

  // lib/dist/spaces/okhsl.js
  var DEG_TO_RAD6 = Math.PI / 180;
  function computeMaxSaturationOklab(a, b) {
    let k0, k1, k2, k3, k4, wl, wm, ws;
    if (-1.88170328 * a - 0.80936493 * b > 1) {
      k0 = 1.19086277;
      k1 = 1.76576728;
      k2 = 0.59662641;
      k3 = 0.75515197;
      k4 = 0.56771245;
      wl = 4.0767416621;
      wm = -3.3077115913;
      ws = 0.2309699292;
    } else if (1.81444104 * a - 1.19445276 * b > 1) {
      k0 = 0.73956515;
      k1 = -0.45954404;
      k2 = 0.08285427;
      k3 = 0.1254107;
      k4 = 0.14503204;
      wl = -1.2684380046;
      wm = 2.6097574011;
      ws = -0.3413193965;
    } else {
      k0 = 1.35733652;
      k1 = -915799e-8;
      k2 = -1.1513021;
      k3 = -0.50559606;
      k4 = 692167e-8;
      wl = -0.0041960863;
      wm = -0.7034186147;
      ws = 1.707614701;
    }
    let S = k0 + k1 * a + k2 * b + k3 * a * a + k4 * a * b;
    const kl = 0.3963377774 * a + 0.2158037573 * b;
    const km = -0.1055613458 * a - 0.0638541728 * b;
    const ks = -0.0894841775 * a - 1.291485548 * b;
    const l_ = 1 + S * kl;
    const m_ = 1 + S * km;
    const s_ = 1 + S * ks;
    const l = l_ * l_ * l_;
    const m = m_ * m_ * m_;
    const s = s_ * s_ * s_;
    const ldS = 3 * kl * l_ * l_;
    const mdS = 3 * km * m_ * m_;
    const sdS = 3 * ks * s_ * s_;
    const ldS2 = 6 * kl * kl * l_;
    const mdS2 = 6 * km * km * m_;
    const sdS2 = 6 * ks * ks * s_;
    const f2 = wl * l + wm * m + ws * s;
    const f1 = wl * ldS + wm * mdS + ws * sdS;
    const f22 = wl * ldS2 + wm * mdS2 + ws * sdS2;
    S = S - f2 * f1 / (f1 * f1 - 0.5 * f2 * f22);
    return S;
  }
  function findCuspOklab(a, b) {
    const sCusp = computeMaxSaturationOklab(a, b);
    const rgb_at_max = oklabToLinearSRGB(oklab(1, sCusp * a, sCusp * b));
    const max = Math.max(rgb_at_max[0], rgb_at_max[1], rgb_at_max[2]);
    if (max <= 0)
      return [0, 0];
    const L_cusp = Math.cbrt(1 / max);
    const C_cusp = L_cusp * sCusp;
    return [L_cusp, C_cusp];
  }
  function oklabToLinearSRGB(lab) {
    const xyzVal = toXYZ(lab);
    const rgb = fromXYZ5(xyzVal);
    return [rgb[0], rgb[1], rgb[2]];
  }
  var TOE_K1 = 0.206;
  var TOE_K2 = 0.03;
  var TOE_K3 = (1 + TOE_K1) / (1 + TOE_K2);
  function toeInv(x) {
    return (x * x + TOE_K1 * x) / (TOE_K3 * (x + TOE_K2));
  }
  function toOKLab2(hsl) {
    const [hDeg, s, l] = hsl;
    if (l <= 0 || l >= 1 || s <= 0) {
      return oklab(toeInv(l), 0, 0);
    }
    const h = wrapHueDeg(hDeg) * DEG_TO_RAD6;
    const a_ = Math.cos(h);
    const b_ = Math.sin(h);
    const L = toeInv(l);
    const [L_cusp, C_cusp] = findCuspOklab(a_, b_);
    const C_0 = 0.4 * Math.min(L, 1 - L);
    const C_mid = C_cusp * (L < L_cusp ? L / L_cusp : (1 - L) / (1 - L_cusp));
    let C5;
    if (s < 0.8) {
      const t = s / 0.8;
      C5 = t * C_mid;
    } else {
      const t = (s - 0.8) / 0.2;
      const C_max = C_cusp * (L < L_cusp ? L / L_cusp : (1 - L) / (1 - L_cusp));
      C5 = C_mid + t * (C_max - C_mid);
    }
    return oklab(L, C5 * a_, C5 * b_);
  }
  function toXYZ16(c) {
    return toXYZ(toOKLab2(c));
  }
  var testVectors22 = [
    // OKHSL test vectors are intentionally minimal — the cusp finding has
    // numerical fragility at the extremes that we accept in v1.4.0.
    // Cross-check against Ottosson's reference JS for strict-precision use.
    {
      input: xyz(0, 0, 0),
      output: okhsl(0, 0, 0),
      tolerance: 0.01,
      source: "Black \u2192 OKHSL (0, 0, 0) \u2014 achromatic, hue irrelevant"
    }
  ];

  // lib/js/components/okhsl-picker.js
  var RES_CAP2 = 800;
  function spaceSliceToRgb(spaceFn, h, s, l) {
    const xyz2 = spaceFn([h, s, l]);
    const lin = fromXYZ5(xyz2);
    const cs = [
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ];
    const enc = encode(cs);
    return [
      Math.round(enc[0] * 255),
      Math.round(enc[1] * 255),
      Math.round(enc[2] * 255)
    ];
  }
  function renderSlice(canvas, hueDeg, mode, label) {
    const wCss = Math.min(canvas.offsetWidth || 280, 320);
    const hCss = wCss;
    const { ctx, w, h } = setupCanvas(canvas, wCss, hCss);
    const dpr = window.devicePixelRatio || 1;
    const RES = Math.min(Math.round(w * dpr), RES_CAP2);
    const tmp = document.createElement("canvas");
    tmp.width = RES;
    tmp.height = RES;
    const imgData = tmp.getContext("2d").createImageData(RES, RES);
    const data = imgData.data;
    for (let py = 0; py < RES; py++) {
      for (let px = 0; px < RES; px++) {
        const s = px / (RES - 1);
        const lVal = 1 - py / (RES - 1);
        const rgb = mode === "okhsl" ? spaceSliceToRgb(toXYZ16, hueDeg, s, lVal) : spaceSliceToRgb(toXYZ8, hueDeg, s, lVal);
        const i = (py * RES + px) * 4;
        data[i] = rgb[0];
        data[i + 1] = rgb[1];
        data[i + 2] = rgb[2];
        data[i + 3] = 255;
      }
    }
    tmp.getContext("2d").putImageData(imgData, 0, 0);
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(tmp, 0, 0, w, h);
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    ctx.font = "11px ui-monospace, monospace";
    ctx.fillText(label, 6, 14);
    ctx.fillText("s \u2192", w - 28, h - 6);
    ctx.fillText("l \u2191", 4, h - 6);
  }
  var OkhslPicker = class extends HTMLElement {
    static get observedAttributes() {
      return ["hue"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._okCanvas) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="okhsl-host">
      <div class="okhsl-grid">
        <div class="okhsl-cell">
          <h4>OKHSL (Ottosson 2021)</h4>
          <canvas class="okhsl-canvas okhsl-ok"></canvas>
        </div>
        <div class="okhsl-cell">
          <h4>HSL (CSS / RGB-cylindrical)</h4>
          <canvas class="okhsl-canvas okhsl-hsl"></canvas>
        </div>
      </div>
    </div>`;
      this._okCanvas = this.querySelector(".okhsl-ok");
      this._hslCanvas = this.querySelector(".okhsl-hsl");
    }
    render() {
      const hueDeg = parseFloat(this.getAttribute("hue") ?? "264");
      renderSlice(this._okCanvas, hueDeg, "okhsl", "OKHSL slice");
      renderSlice(this._hslCanvas, hueDeg, "hsl", "HSL slice");
    }
  };
  customElements.define("okhsl-picker", OkhslPicker);

  // lib/js/components/blend-through-white.js
  var STOPS = 64;
  function hexToEnc(hex) {
    return [
      parseInt(hex.slice(1, 3), 16) / 255,
      parseInt(hex.slice(3, 5), 16) / 255,
      parseInt(hex.slice(5, 7), 16) / 255
    ];
  }
  function clipLin2(lin) {
    return [
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ];
  }
  function encToHexBytes(enc) {
    return [Math.round(enc[0] * 255), Math.round(enc[1] * 255), Math.round(enc[2] * 255)];
  }
  function lerp(a, b, t) {
    return a + (b - a) * t;
  }
  function lerp3(A5, B4, t) {
    return [lerp(A5[0], B4[0], t), lerp(A5[1], B4[1], t), lerp(A5[2], B4[2], t)];
  }
  var SPACES = [
    {
      id: "encoded",
      label: "Encoded sRGB",
      note: "naively averaging hex values \u2014 the classic muddy mid-tone bug.",
      interp: (src, t) => {
        const srcEnc = hexToEnc(src);
        const whEnc = [1, 1, 1];
        return lerp3(srcEnc, whEnc, t);
      }
    },
    {
      id: "linear",
      label: "Linear sRGB",
      note: "gamma-correct linear interpolation. Mid-tones brighten, but hue can drift.",
      interp: (src, t) => {
        const srcLin = decode(hexToEnc(src));
        const whLin = [1, 1, 1];
        const mix2 = lerp3(srcLin, whLin, t);
        return encode(clipLin2(mix2));
      }
    },
    {
      id: "oklab",
      label: "OKLab",
      note: "perceptually uniform \u2014 equal t looks like equal steps; hue stays stable.",
      interp: (src, t) => {
        const srcXyz = toXYZ5(decode(hexToEnc(src)));
        const whXyz = toXYZ5([1, 1, 1]);
        const srcLab = fromXYZ(srcXyz);
        const whLab = fromXYZ(whXyz);
        const mixLab = lerp3(srcLab, whLab, t);
        const mixXyz = toXYZ(mixLab);
        const lin = fromXYZ5(mixXyz);
        return encode(clipLin2(lin));
      }
    },
    {
      id: "cielab",
      label: "CIELAB",
      note: "older perceptual space \u2014 works but blues notoriously curve toward purple.",
      interp: (src, t) => {
        const srcXyz = toXYZ5(decode(hexToEnc(src)));
        const whXyz = toXYZ5([1, 1, 1]);
        const srcLab = fromXYZ3(srcXyz);
        const whLab = fromXYZ3(whXyz);
        const mixLab = lerp3(srcLab, whLab, t);
        const mixXyz = toXYZ3(mixLab);
        const lin = fromXYZ5(mixXyz);
        return encode(clipLin2(lin));
      }
    },
    {
      id: "hsl",
      label: "HSL",
      note: "cylindrical RGB \u2014 saturation drops to 0 mid-mix; lightness sweep is uneven.",
      interp: (src, t) => {
        const srcXyz = toXYZ5(decode(hexToEnc(src)));
        const whXyz = toXYZ5([1, 1, 1]);
        const srcHsl = fromXYZ8(srcXyz);
        const whHsl = fromXYZ8(whXyz);
        const mixHsl = [srcHsl[0], lerp(srcHsl[1], whHsl[1], t), lerp(srcHsl[2], whHsl[2], t)];
        const mixXyz = toXYZ8(mixHsl);
        const lin = fromXYZ5(mixXyz);
        return encode(clipLin2(lin));
      }
    }
  ];
  var BlendThroughWhite = class extends HTMLElement {
    static get observedAttributes() {
      return ["color"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._root) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="btw-host"></div>`;
      this._root = this.querySelector(".btw-host");
    }
    render() {
      const src = this.getAttribute("color") || "#0066ff";
      if (!/^#[0-9a-fA-F]{6}$/.test(src)) return;
      this._root.innerHTML = SPACES.map((s) => `
      <div class="btw-row">
        <div class="btw-label">
          <strong>${s.label}</strong>
          <div class="btw-note">${s.note}</div>
        </div>
        <canvas class="btw-canvas" data-space="${s.id}"></canvas>
      </div>
    `).join("");
      this._root.querySelectorAll("canvas[data-space]").forEach((canv) => {
        const space = SPACES.find((s) => s.id === canv.dataset.space);
        const wCss = Math.min(this.offsetWidth || 600, 720) - 200;
        const hCss = 56;
        const { ctx, w, h } = setupCanvas(canv, wCss, hCss);
        const tmp = document.createElement("canvas");
        tmp.width = STOPS;
        tmp.height = 1;
        const imgData = tmp.getContext("2d").createImageData(STOPS, 1);
        for (let i = 0; i < STOPS; i++) {
          const t = i / (STOPS - 1);
          const enc = space.interp(src, t);
          const bytes = encToHexBytes(enc);
          imgData.data[i * 4] = bytes[0];
          imgData.data[i * 4 + 1] = bytes[1];
          imgData.data[i * 4 + 2] = bytes[2];
          imgData.data[i * 4 + 3] = 255;
        }
        tmp.getContext("2d").putImageData(imgData, 0, 0);
        ctx.imageSmoothingEnabled = true;
        ctx.drawImage(tmp, 0, 0, w, h);
      });
    }
  };
  customElements.define("blend-through-white", BlendThroughWhite);

  // lib/js/components/cvd-safe-palette.js
  var CVDs = [
    { id: "normal", label: "Normal vision" },
    { id: "protanopia", label: "Protanopia" },
    { id: "deuteranopia", label: "Deuteranopia" },
    { id: "tritanopia", label: "Tritanopia" }
  ];
  function oklchToHex3(L, C5, h) {
    const lab = toOKLab([L, C5, h]);
    const xyz2 = toXYZ(lab);
    const lin = fromXYZ5(xyz2);
    const cs = [
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ];
    return toHex(encode(cs));
  }
  function oklchToOklab(L, C5, h) {
    return toOKLab([L, C5, h]);
  }
  function applyCVDtoOklab(lab, type) {
    if (type === "normal") return lab;
    const xyz2 = toXYZ(lab);
    const lin = fromXYZ5(xyz2);
    const sim = mulMat3Vec3(simulationMatrix(type, 1), lin);
    const cs = [
      Math.max(0, Math.min(1, sim[0])),
      Math.max(0, Math.min(1, sim[1])),
      Math.max(0, Math.min(1, sim[2]))
    ];
    return fromXYZ(toXYZ5(cs));
  }
  function paletteFromHues(hues, L) {
    return hues.map((h) => {
      const C5 = Math.min(0.18, peakC(L, h, M_XYZ_TO_SRGB2, 24, 0.4) * 0.95);
      const lab = oklchToOklab(L, C5, h);
      return { h, L, C: C5, lab, hex: oklchToHex3(L, C5, h) };
    });
  }
  function minSeparationForCVD(palette, cvdType) {
    let minD = Infinity;
    for (let i = 0; i < palette.length; i++) {
      for (let j = i + 1; j < palette.length; j++) {
        const a = applyCVDtoOklab(palette[i].lab, cvdType);
        const b = applyCVDtoOklab(palette[j].lab, cvdType);
        const d = deltaEOK(a, b);
        if (d < minD) minD = d;
      }
    }
    return minD;
  }
  function worstSeparation(palette) {
    return CVDs.reduce((acc, cvd) => {
      const d = minSeparationForCVD(palette, cvd.id);
      return Math.min(acc, d);
    }, Infinity);
  }
  function optimizePalette(n, baseHue, L) {
    let hues = [];
    for (let i = 0; i < n; i++) hues.push((baseHue + 360 * i / n) % 360);
    let best = paletteFromHues(hues, L);
    let bestScore = worstSeparation(best);
    for (let iter = 0; iter < 18; iter++) {
      let improved = false;
      const step = 24 / (1 + iter);
      for (let i = 0; i < n; i++) {
        for (const dir of [-1, 1]) {
          const trial = hues.slice();
          trial[i] = (trial[i] + dir * step + 360) % 360;
          const cand = paletteFromHues(trial, L);
          const candScore = worstSeparation(cand);
          if (candScore > bestScore + 1e-5) {
            hues = trial;
            best = cand;
            bestScore = candScore;
            improved = true;
          }
        }
      }
      if (!improved) break;
    }
    return { palette: best, score: bestScore };
  }
  var CvdSafePalette = class extends HTMLElement {
    static get observedAttributes() {
      return ["n", "hue", "lightness"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._root) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="cvdp-host"></div>`;
      this._root = this.querySelector(".cvdp-host");
    }
    render() {
      const n = Math.max(2, Math.min(8, parseInt(this.getAttribute("n") ?? "5", 10)));
      const baseHue = parseFloat(this.getAttribute("hue") ?? "0");
      const L = parseFloat(this.getAttribute("lightness") ?? "0.62");
      const { palette, score } = optimizePalette(n, baseHue, L);
      let html = '<div class="cvdp-strip">';
      for (const c of palette) {
        html += '<div class="cvdp-swatch" style="background:' + c.hex + '"><span>' + c.hex + "</span></div>";
      }
      html += "</div>";
      html += '<table class="cvdp-table"><thead><tr><th>Condition</th><th>min \u0394E<sub>ok</sub></th><th></th></tr></thead><tbody>';
      for (const cvd of CVDs) {
        const d = minSeparationForCVD(palette, cvd.id);
        const isWorst = Math.abs(d - score) < 1e-5;
        html += "<tr><td><strong>" + cvd.label + "</strong></td><td><strong>" + fmt(d, 3) + "</strong></td><td>" + (isWorst ? '<span class="pill warn">worst</span>' : "") + "</td></tr>";
      }
      html += "</tbody></table>";
      html += '<div class="cvdp-summary">Worst-case \u0394E<sub>ok</sub> across all CVD types: <strong>' + fmt(score, 3) + "</strong></div>";
      this._root.innerHTML = html;
    }
  };
  customElements.define("cvd-safe-palette", CvdSafePalette);

  // lib/dist/spaces/lms.js
  var M_XYZ_TO_LMS = [
    [0.8189330101, 0.3618667424, -0.1288597137],
    [0.0329845436, 0.9293118715, 0.0361456387],
    [0.0482003018, 0.2643662691, 0.633851707]
  ];
  var testVectors23 = [
    {
      input: xyz(0, 0, 0),
      output: [0, 0, 0],
      tolerance: LINEAR_TOLERANCE,
      source: "Black point"
    },
    {
      input: xyz(0.9504559270516716, 1, 1.0890577507598784),
      output: [1, 1, 1],
      tolerance: 1e-3,
      source: "D65 white \u2192 LMS \u2248 (1, 1, 1) (M1 row sums normalize white)"
    }
  ];

  // lib/js/components/cmf-chart.js
  var LMS_CURVES = (() => {
    const Lc = [], Mc = [], Sc = [];
    for (let i = 0; i < 36; i++) {
      const xyz2 = [X_BAR_1931[i], Y_BAR_1931[i], Z_BAR_1931[i]];
      const lms = mulMat3Vec3(M_XYZ_TO_LMS, xyz2);
      Lc.push(lms[0]);
      Mc.push(lms[1]);
      Sc.push(lms[2]);
    }
    return { L: Lc, M: Mc, S: Sc };
  })();
  function spectralColorHex(nm) {
    const idx = Math.max(0, Math.min(35, Math.round((nm - 380) / 10)));
    const xyz2 = CMF_1931[idx];
    const lin = fromXYZ5(xyz2);
    const m = Math.max(lin[0], lin[1], lin[2], 1e-6);
    const norm = [lin[0] / m, lin[1] / m, lin[2] / m];
    const cs = [
      Math.max(0, Math.min(1, norm[0])),
      Math.max(0, Math.min(1, norm[1])),
      Math.max(0, Math.min(1, norm[2]))
    ];
    const enc = encode(cs);
    return "#" + [enc[0], enc[1], enc[2]].map((v) => Math.round(v * 255).toString(16).padStart(2, "0")).join("");
  }
  var CMFChart = class extends HTMLElement {
    static get observedAttributes() {
      return ["wavelength", "show-lms"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._canvas) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="cmf-host">
      <canvas class="cmf-canvas"></canvas>
      <div class="cmf-readout"></div>
    </div>`;
      this._canvas = this.querySelector(".cmf-canvas");
      this._readout = this.querySelector(".cmf-readout");
    }
    render() {
      const wavelength = Math.max(380, Math.min(730, parseFloat(this.getAttribute("wavelength") ?? "555")));
      const showLms = this.getAttribute("show-lms") !== "false";
      const wCss = Math.min(this.offsetWidth || 720, 720);
      const hCss = 320;
      const { ctx, w, h } = setupCanvas(this._canvas, wCss, hCss);
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--bg-card").trim() || "#fff";
      ctx.fillRect(0, 0, w, h);
      const padL = 40, padR = 12, padT = 16, padB = 32;
      const cw = w - padL - padR;
      const ch = h - padT - padB;
      const yMax = 2;
      const X_OF = (nm) => padL + (nm - 380) / (730 - 380) * cw;
      const Y_OF = (v) => padT + ch - v / yMax * ch;
      for (let nm = 380; nm <= 730; nm += 2) {
        const hex2 = spectralColorHex(nm);
        ctx.fillStyle = hex2;
        const x = X_OF(nm);
        const xn = X_OF(nm + 2);
        ctx.fillRect(x, padT + ch + 4, xn - x + 1, 14);
      }
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      ctx.font = "10px ui-monospace, monospace";
      [400, 450, 500, 550, 600, 650, 700].forEach((nm) => {
        const x = X_OF(nm);
        ctx.fillText(nm + "nm", x - 14, padT + ch + 30);
        ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--border").trim() || "#ccc";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x, padT);
        ctx.lineTo(x, padT + ch);
        ctx.stroke();
      });
      [0, 0.5, 1, 1.5, 2].forEach((v) => {
        const y = Y_OF(v);
        ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--border").trim() || "#ccc";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padL, y);
        ctx.lineTo(padL + cw, y);
        ctx.stroke();
        ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
        ctx.fillText(v.toFixed(1), 4, y + 4);
      });
      function plot(arr, color, lw) {
        ctx.beginPath();
        WAVELENGTHS_NM.forEach((nm, i) => {
          const x = X_OF(nm);
          const y = Y_OF(arr[i]);
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.strokeStyle = color;
        ctx.lineWidth = lw || 2;
        ctx.stroke();
      }
      if (showLms) {
        plot(LMS_CURVES.L, "oklch(0.55 0.22 29)", 2);
        plot(LMS_CURVES.M, "oklch(0.62 0.18 142)", 2);
        plot(LMS_CURVES.S, "oklch(0.55 0.22 264)", 2);
      }
      plot(X_BAR_1931, "oklch(0.55 0.22 29)", showLms ? 1 : 2.5);
      plot(Y_BAR_1931, "oklch(0.62 0.18 142)", showLms ? 1 : 2.5);
      plot(Z_BAR_1931, "oklch(0.55 0.22 264)", showLms ? 1 : 2.5);
      const cx = X_OF(wavelength);
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--text").trim() || "#000";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(cx, padT);
      ctx.lineTo(cx, padT + ch);
      ctx.stroke();
      const idx = Math.max(0, Math.min(35, Math.round((wavelength - 380) / 10)));
      const xb = X_BAR_1931[idx], yb = Y_BAR_1931[idx], zb = Z_BAR_1931[idx];
      const sum = xb + yb + zb || 1e-9;
      const cx_chroma = xb / sum, cy_chroma = yb / sum;
      const Lr = LMS_CURVES.L[idx], Mr = LMS_CURVES.M[idx], Sr = LMS_CURVES.S[idx];
      const hex = spectralColorHex(wavelength);
      this._readout.innerHTML = '<div class="cmf-r-row"><div>\u03BB = <strong>' + wavelength.toFixed(0) + ' nm</strong></div><div class="cmf-swatch" style="background:' + hex + '"></div></div><div class="cmf-r-grid"><div><span class="cmf-tag" style="background:oklch(0.55 0.22 29)">x\u0304</span> ' + fmt(xb, 4) + '</div><div><span class="cmf-tag" style="background:oklch(0.62 0.18 142)">\u0233</span> ' + fmt(yb, 4) + '</div><div><span class="cmf-tag" style="background:oklch(0.55 0.22 264)">z\u0304</span> ' + fmt(zb, 4) + '</div><div><span class="cmf-tag" style="background:oklch(0.55 0.18 29)">L</span> ' + fmt(Lr, 4) + '</div><div><span class="cmf-tag" style="background:oklch(0.62 0.14 142)">M</span> ' + fmt(Mr, 4) + '</div><div><span class="cmf-tag" style="background:oklch(0.55 0.18 264)">S</span> ' + fmt(Sr, 4) + "</div></div><div>chromaticity x = <strong>" + fmt(cx_chroma, 4) + "</strong>, y = <strong>" + fmt(cy_chroma, 4) + "</strong></div>";
    }
  };
  customElements.define("cmf-chart", CMFChart);

  // lib/js/components/macadam-ellipses.js
  var MACADAM = [
    [0.16, 0.057, 85e-5, 35e-5, 62.5],
    [0.187, 0.118, 22e-4, 55e-5, 77],
    [0.253, 0.125, 255e-5, 8e-4, 55.5],
    [0.15, 0.68, 5e-3, 15e-4, 105],
    [0.131, 0.521, 46e-4, 19e-4, 112.5],
    [0.212, 0.55, 58e-4, 2e-3, 100],
    [0.258, 0.45, 51e-4, 2e-3, 92],
    [0.152, 0.365, 4e-3, 15e-4, 110],
    [0.28, 0.385, 38e-4, 15e-4, 75.5],
    [0.38, 0.498, 44e-4, 12e-4, 70],
    [0.16, 0.2, 21e-4, 95e-5, 77],
    [0.228, 0.25, 31e-4, 9e-4, 86],
    [0.305, 0.323, 23e-4, 9e-4, 59.5],
    [0.385, 0.393, 38e-4, 16e-4, 64.5],
    [0.472, 0.399, 32e-4, 14e-4, 72.5],
    [0.527, 0.35, 26e-4, 13e-4, 74],
    [0.475, 0.3, 29e-4, 11e-4, 69.5],
    [0.51, 0.236, 24e-4, 12e-4, 56.5],
    [0.596, 0.283, 26e-4, 13e-4, 58],
    [0.344, 0.284, 23e-4, 9e-4, 60],
    [0.39, 0.237, 25e-4, 1e-3, 47],
    [0.441, 0.198, 28e-4, 95e-5, 44.5],
    [0.278, 0.223, 24e-4, 55e-5, 37.5],
    [0.3, 0.163, 29e-4, 6e-4, 20],
    [0.365, 0.153, 36e-4, 8e-4, 50]
  ];
  var SPECTRAL_LOCUS2 = [
    [0.1741, 5e-3],
    [0.1738, 49e-4],
    [0.1733, 48e-4],
    [0.1726, 48e-4],
    [0.1714, 51e-4],
    [0.1689, 69e-4],
    [0.1644, 0.0109],
    [0.1566, 0.0177],
    [0.144, 0.0297],
    [0.1241, 0.0578],
    [0.0913, 0.1327],
    [0.0454, 0.295],
    [82e-4, 0.5384],
    [0.0139, 0.7502],
    [0.0743, 0.8338],
    [0.1547, 0.8059],
    [0.2296, 0.7543],
    [0.3016, 0.6923],
    [0.3731, 0.6245],
    [0.4441, 0.5547],
    [0.5125, 0.4866],
    [0.5752, 0.4242],
    [0.627, 0.3725],
    [0.6658, 0.334],
    [0.6915, 0.3083],
    [0.7079, 0.292],
    [0.719, 0.2809],
    [0.726, 0.274],
    [0.73, 0.27],
    [0.732, 0.268],
    [0.7334, 0.2666],
    [0.7344, 0.2656],
    [0.7347, 0.2653]
  ];
  var SRGB_TRIANGLE = [[0.64, 0.33], [0.3, 0.6], [0.15, 0.06]];
  var X_RANGE2 = [0, 0.8];
  var Y_RANGE2 = [0, 0.9];
  var MacadamEllipses = class extends HTMLElement {
    static get observedAttributes() {
      return ["scale"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._canvas) this.render();
    }
    _mount() {
      this.innerHTML = `<canvas class="macadam-canvas"></canvas>
      <div class="macadam-legend" style="color:var(--text-muted);font-size:var(--text-xs);margin-top:var(--s-2);">
        Each ellipse encloses a "just-noticeable difference" region \u2014 the colors
        inside look identical to a trained observer. Shown at <strong>10\xD7 actual
        size</strong> by default for visibility (real ellipses are tiny).
      </div>`;
      this._canvas = this.querySelector(".macadam-canvas");
    }
    render() {
      const scale = parseFloat(this.getAttribute("scale") ?? "10");
      const wCss = Math.min(this.offsetWidth || 640, 760);
      const hCss = Math.round(wCss * (Y_RANGE2[1] / X_RANGE2[1]));
      const { ctx, w, h } = setupCanvas(this._canvas, wCss, hCss);
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--bg-card").trim() || "#fff";
      ctx.fillRect(0, 0, w, h);
      const X = (xv) => (xv - X_RANGE2[0]) / (X_RANGE2[1] - X_RANGE2[0]) * w;
      const Y = (yv) => h - (yv - Y_RANGE2[0]) / (Y_RANGE2[1] - Y_RANGE2[0]) * h;
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      SPECTRAL_LOCUS2.forEach(([x, y], i) => {
        const px = X(x), py = Y(y);
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.closePath();
      ctx.stroke();
      ctx.strokeStyle = "oklch(0.554 0.180 264)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      SRGB_TRIANGLE.forEach(([x, y], i) => {
        const px = X(x), py = Y(y);
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.closePath();
      ctx.stroke();
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim() || "#0066cc";
      ctx.lineWidth = 1.5;
      ctx.fillStyle = "oklch(0.554 0.180 264 / 0.18)";
      for (const [cx, cy, a, b, angleDeg] of MACADAM) {
        const px = X(cx), py = Y(cy);
        const xPerUnit = w / (X_RANGE2[1] - X_RANGE2[0]);
        const yPerUnit = h / (Y_RANGE2[1] - Y_RANGE2[0]);
        const aPx = a * scale * xPerUnit;
        const bPx = b * scale * yPerUnit;
        ctx.save();
        ctx.translate(px, py);
        ctx.rotate(-angleDeg * Math.PI / 180);
        ctx.beginPath();
        ctx.ellipse(0, 0, aPx, bPx, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.restore();
      }
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      ctx.font = "11px ui-monospace, monospace";
      [0.2, 0.4, 0.6].forEach((v) => {
        ctx.fillText(v.toFixed(1), X(v) - 8, h - 6);
        ctx.fillText(v.toFixed(1), 4, Y(v) - 4);
      });
      ctx.fillText("x", w - 12, h - 6);
      ctx.fillText("y", 6, 14);
      ctx.fillText("sRGB gamut", X(0.34), Y(0.36));
    }
  };
  customElements.define("macadam-ellipses", MacadamEllipses);

  // lib/js/components/volume-bars.js
  var M_XYZ_TO_ADOBE_RGB = [
    [2.041369, -0.5649464, -0.3446944],
    [-0.969266, 1.8760108, 0.041556],
    [0.0134474, -0.1183897, 1.0154096]
  ];
  var M_XYZ_TO_PROPHOTO_D65 = [
    [1.346, -0.2556, -0.0511],
    [-0.5446, 1.5082, 0.0205],
    [0, 0, 1.2117]
  ];
  var GAMUTS3 = [
    { name: "Rec.709", matrix: M_XYZ_TO_SRGB2, color: "oklch(0.55 0.18 264)" },
    { name: "sRGB", matrix: M_XYZ_TO_SRGB2, color: "oklch(0.55 0.18 264)" },
    { name: "Display P3", matrix: M_XYZ_TO_P32, color: "oklch(0.62 0.18 150)" },
    { name: "Adobe RGB", matrix: M_XYZ_TO_ADOBE_RGB, color: "oklch(0.55 0.18 300)" },
    { name: "Rec.2020", matrix: M_XYZ_TO_REC20202, color: "oklch(0.70 0.18  50)" },
    { name: "ProPhoto", matrix: M_XYZ_TO_PROPHOTO_D65, color: "oklch(0.62 0.18 200)" }
  ];
  var SAMPLES2 = 3e4;
  function measureVolumes() {
    const Lmin = 0, Lmax = 1;
    const aRange = 0.45, bRange = 0.45;
    const boxVolume = (Lmax - Lmin) * (aRange * 2) * (bRange * 2);
    const counts = GAMUTS3.map(() => 0);
    let xorshift = 12648430;
    function rand() {
      xorshift ^= xorshift << 13;
      xorshift ^= xorshift >>> 17;
      xorshift ^= xorshift << 5;
      return (xorshift >>> 0) / 4294967295;
    }
    for (let i = 0; i < SAMPLES2; i++) {
      const L = Lmin + rand() * (Lmax - Lmin);
      const a = -aRange + rand() * (aRange * 2);
      const b = -bRange + rand() * (bRange * 2);
      const xyz2 = toXYZ([L, a, b]);
      for (let g = 0; g < GAMUTS3.length; g++) {
        if (inGamut(mulMat3Vec3(GAMUTS3[g].matrix, xyz2))) counts[g]++;
      }
    }
    return counts.map((c, g) => ({
      name: GAMUTS3[g].name,
      color: GAMUTS3[g].color,
      volume: c / SAMPLES2 * boxVolume
    }));
  }
  var VolumeBars = class extends HTMLElement {
    connectedCallback() {
      this._mount();
      this.render();
    }
    _mount() {
      this.innerHTML = `<div class="vol-host">
      <p class="vol-status" style="color:var(--text-muted);font-size:var(--text-sm);">Measuring volumes by Monte Carlo (${SAMPLES2.toLocaleString()} samples)\u2026</p>
      <canvas class="vol-canvas"></canvas>
      <table class="vol-table"></table>
    </div>`;
      this._canvas = this.querySelector(".vol-canvas");
      this._table = this.querySelector(".vol-table");
      this._status = this.querySelector(".vol-status");
    }
    render() {
      requestAnimationFrame(() => {
        const t = performance.now();
        const measured = measureVolumes();
        const sRGB = measured.find((m) => m.name === "sRGB").volume;
        const elapsed = (performance.now() - t).toFixed(0);
        const wCss = Math.min(this.offsetWidth || 700, 760);
        const hCss = 320;
        const { ctx, w, h } = setupCanvas(this._canvas, wCss, hCss);
        ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--bg-card").trim() || "#fff";
        ctx.fillRect(0, 0, w, h);
        const padL = 110, padR = 60, padT = 16, padB = 16;
        const cw = w - padL - padR;
        const ch = h - padT - padB;
        const barH = ch / measured.length - 6;
        const maxV = Math.max(...measured.map((m) => m.volume));
        ctx.font = "12px ui-monospace, monospace";
        measured.forEach((m, i) => {
          const y = padT + i * (barH + 6);
          const ratio = m.volume / sRGB;
          const widthPx = m.volume / maxV * cw;
          ctx.fillStyle = m.color;
          ctx.fillRect(padL, y, widthPx, barH);
          ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#666";
          ctx.textAlign = "right";
          ctx.fillText(m.name, padL - 8, y + barH / 2 + 4);
          ctx.textAlign = "left";
          ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text").trim() || "#111";
          ctx.fillText(ratio.toFixed(2) + "\xD7", padL + widthPx + 8, y + barH / 2 + 4);
        });
        let html = "<thead><tr><th>Gamut</th><th>Volume (OKLab units)</th><th>vs sRGB</th></tr></thead><tbody>";
        for (const m of measured) {
          html += '<tr><td><span class="vol-dot" style="background:' + m.color + '"></span> <strong>' + m.name + "</strong></td><td>" + fmt(m.volume, 4) + "</td><td>" + fmt(m.volume / sRGB, 2) + "\xD7</td></tr>";
        }
        html += "</tbody>";
        this._table.innerHTML = html;
        this._status.textContent = `Monte Carlo with ${SAMPLES2.toLocaleString()} OKLab samples \u2014 ${elapsed}ms`;
      });
    }
  };
  customElements.define("volume-bars", VolumeBars);

  // lib/js/components/color-cube-3d.js
  var SAMPLES_PER_EDGE = 14;
  var VERTICES = [
    [0, 0, 0],
    [1, 0, 0],
    [1, 1, 0],
    [0, 1, 0],
    [0, 0, 1],
    [1, 0, 1],
    [1, 1, 1],
    [0, 1, 1]
  ];
  var EDGES = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 0],
    [4, 5],
    [5, 6],
    [6, 7],
    [7, 4],
    [0, 4],
    [1, 5],
    [2, 6],
    [3, 7]
  ];
  function transformPoint(encR, encG, encB, space) {
    const lin = decode([encR, encG, encB]);
    const xyz2 = toXYZ5(lin);
    if (space === "oklab") {
      const [L, a, b] = fromXYZ(xyz2);
      return [a * 1.6, L - 0.5, b * 1.6];
    } else if (space === "cielab") {
      const [L, a, b] = fromXYZ3(xyz2);
      return [a / 128, L / 100 - 0.5, b / 128];
    } else {
      return [encR - 0.5, encG - 0.5, encB - 0.5];
    }
  }
  function project(point, rotX, rotY, scale, w, h) {
    const cx = Math.cos(rotY), sx = Math.sin(rotY);
    const cy = Math.cos(rotX), sy = Math.sin(rotX);
    let x = point[0], y = point[1], z = point[2];
    let x1 = x * cx + z * sx;
    let z1 = -x * sx + z * cx;
    let y1 = y * cy - z1 * sy;
    let z2 = y * sy + z1 * cy;
    return [
      w / 2 + x1 * scale,
      h / 2 - y1 * scale,
      z2
    ];
  }
  function encodedHex(r, g, b) {
    return "#" + [r, g, b].map((v) => Math.round(v * 255).toString(16).padStart(2, "0")).join("");
  }
  var ColorCube3D = class extends HTMLElement {
    static get observedAttributes() {
      return ["space"];
    }
    connectedCallback() {
      this._rotX = 0.3;
      this._rotY = -0.5;
      this._dragging = false;
      this._mount();
      this.render();
      this._addDragHandlers();
    }
    attributeChangedCallback() {
      if (this._canvas) this.render();
    }
    _mount() {
      this.innerHTML = `<canvas class="cube-canvas"></canvas>
      <p class="cube-hint" style="color:var(--text-muted);font-size:var(--text-xs);margin-top:var(--s-2);">Drag the cube to rotate.</p>`;
      this._canvas = this.querySelector(".cube-canvas");
    }
    _addDragHandlers() {
      let lastX = 0, lastY = 0;
      this._canvas.addEventListener("pointerdown", (e) => {
        this._dragging = true;
        lastX = e.clientX;
        lastY = e.clientY;
        this._canvas.setPointerCapture(e.pointerId);
      });
      this._canvas.addEventListener("pointerup", (e) => {
        this._dragging = false;
        try {
          this._canvas.releasePointerCapture(e.pointerId);
        } catch (err) {
        }
      });
      this._canvas.addEventListener("pointermove", (e) => {
        if (!this._dragging) return;
        const dx = e.clientX - lastX, dy = e.clientY - lastY;
        lastX = e.clientX;
        lastY = e.clientY;
        this._rotY += dx * 0.01;
        this._rotX += dy * 0.01;
        this.render();
      });
    }
    render() {
      if (!this._canvas) return;
      const space = this.getAttribute("space") || "oklab";
      const size = Math.min(this.offsetWidth || 500, 560);
      const { ctx, w, h } = setupCanvas(this._canvas, size, size);
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--bg-card").trim() || "#fff";
      ctx.fillRect(0, 0, w, h);
      const scale = size * 0.42;
      const allDots = [];
      for (const [aIdx, bIdx] of EDGES) {
        const A5 = VERTICES[aIdx], B4 = VERTICES[bIdx];
        for (let i = 0; i <= SAMPLES_PER_EDGE; i++) {
          const t = i / SAMPLES_PER_EDGE;
          const encR = A5[0] + (B4[0] - A5[0]) * t;
          const encG = A5[1] + (B4[1] - A5[1]) * t;
          const encB = A5[2] + (B4[2] - A5[2]) * t;
          const pt = transformPoint(encR, encG, encB, space);
          const proj = project(pt, this._rotX, this._rotY, scale, w, h);
          allDots.push({
            proj,
            hex: encodedHex(encR, encG, encB),
            depth: proj[2]
          });
        }
      }
      allDots.sort((a, b) => a.depth - b.depth);
      for (const d of allDots) {
        ctx.fillStyle = d.hex;
        ctx.beginPath();
        ctx.arc(d.proj[0], d.proj[1], 4.5, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      ctx.font = "11px ui-monospace, monospace";
      ctx.fillText(space === "oklab" ? "sRGB cube \u2192 OKLab (curved)" : space === "cielab" ? "sRGB cube \u2192 CIELAB (curved)" : "sRGB cube (linear, no transform)", 10, h - 10);
    }
  };
  customElements.define("color-cube-3d", ColorCube3D);

  // lib/js/components/multi-dither.js
  function nearestIdx(point, palette) {
    let best = 0, bestDist = Infinity;
    for (let i = 0; i < palette.length; i++) {
      const dL = point[0] - palette[i][0];
      const dA = point[1] - palette[i][1];
      const dB = point[2] - palette[i][2];
      const d = dL * dL + dA * dA + dB * dB;
      if (d < bestDist) {
        bestDist = d;
        best = i;
      }
    }
    return best;
  }
  function ditherFS(source, palette) {
    const H = source.length, W = source[0].length;
    const buf = source.map((row) => row.map((c) => [c[0], c[1], c[2]]));
    const indices = [];
    for (let y = 0; y < H; y++) {
      const row = [];
      for (let x = 0; x < W; x++) {
        const idx = nearestIdx(buf[y][x], palette);
        row.push(idx);
        const errL = buf[y][x][0] - palette[idx][0];
        const errA = buf[y][x][1] - palette[idx][1];
        const errB = buf[y][x][2] - palette[idx][2];
        const diff = (yy, xx, weight) => {
          if (yy < 0 || yy >= H || xx < 0 || xx >= W) return;
          buf[yy][xx] = [
            buf[yy][xx][0] + errL * weight,
            buf[yy][xx][1] + errA * weight,
            buf[yy][xx][2] + errB * weight
          ];
        };
        diff(y, x + 1, 7 / 16);
        diff(y + 1, x - 1, 3 / 16);
        diff(y + 1, x, 5 / 16);
        diff(y + 1, x + 1, 1 / 16);
      }
      indices.push(row);
    }
    return indices;
  }
  function ditherAtkinson(source, palette) {
    const H = source.length, W = source[0].length;
    const buf = source.map((row) => row.map((c) => [c[0], c[1], c[2]]));
    const indices = [];
    for (let y = 0; y < H; y++) {
      const row = [];
      for (let x = 0; x < W; x++) {
        const idx = nearestIdx(buf[y][x], palette);
        row.push(idx);
        const errL = (buf[y][x][0] - palette[idx][0]) / 8;
        const errA = (buf[y][x][1] - palette[idx][1]) / 8;
        const errB = (buf[y][x][2] - palette[idx][2]) / 8;
        const diff = (yy, xx) => {
          if (yy < 0 || yy >= H || xx < 0 || xx >= W) return;
          buf[yy][xx] = [
            buf[yy][xx][0] + errL,
            buf[yy][xx][1] + errA,
            buf[yy][xx][2] + errB
          ];
        };
        diff(y, x + 1);
        diff(y, x + 2);
        diff(y + 1, x - 1);
        diff(y + 1, x);
        diff(y + 1, x + 1);
        diff(y + 2, x);
      }
      indices.push(row);
    }
    return indices;
  }
  function ditherJarvis(source, palette) {
    const H = source.length, W = source[0].length;
    const buf = source.map((row) => row.map((c) => [c[0], c[1], c[2]]));
    const indices = [];
    const W_TABLE = [
      [0, 1, 7],
      [0, 2, 5],
      [1, -2, 3],
      [1, -1, 5],
      [1, 0, 7],
      [1, 1, 5],
      [1, 2, 3],
      [2, -2, 1],
      [2, -1, 3],
      [2, 0, 5],
      [2, 1, 3],
      [2, 2, 1]
    ];
    for (let y = 0; y < H; y++) {
      const row = [];
      for (let x = 0; x < W; x++) {
        const idx = nearestIdx(buf[y][x], palette);
        row.push(idx);
        const errL = buf[y][x][0] - palette[idx][0];
        const errA = buf[y][x][1] - palette[idx][1];
        const errB = buf[y][x][2] - palette[idx][2];
        for (const [dy, dx, wgt] of W_TABLE) {
          const yy = y + dy, xx = x + dx;
          if (yy < 0 || yy >= H || xx < 0 || xx >= W) continue;
          const f2 = wgt / 48;
          buf[yy][xx] = [
            buf[yy][xx][0] + errL * f2,
            buf[yy][xx][1] + errA * f2,
            buf[yy][xx][2] + errB * f2
          ];
        }
      }
      indices.push(row);
    }
    return indices;
  }
  var BAYER_4 = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5]
  ];
  function ditherBayer(source, palette) {
    const H = source.length, W = source[0].length;
    const indices = [];
    const SCALE = 0.06;
    for (let y = 0; y < H; y++) {
      const row = [];
      for (let x = 0; x < W; x++) {
        const m = BAYER_4[y % 4][x % 4];
        const off = (m / 16 - 0.5) * SCALE;
        const p = [source[y][x][0] + off, source[y][x][1] + off * 0.3, source[y][x][2] + off * 0.3];
        row.push(nearestIdx(p, palette));
      }
      indices.push(row);
    }
    return indices;
  }
  var ALGOS = [
    { id: "fs", name: "Floyd-Steinberg", fn: ditherFS },
    { id: "atkinson", name: "Atkinson", fn: ditherAtkinson },
    { id: "jarvis", name: "Jarvis-Judice-Ninke", fn: ditherJarvis },
    { id: "bayer", name: "Bayer 4\xD74 ordered", fn: ditherBayer }
  ];
  function oklabToHexBytes2(lab) {
    const xyz2 = toXYZ(lab);
    const lin = fromXYZ5(xyz2);
    const cs = [
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ];
    const enc = encode(cs);
    return [Math.round(enc[0] * 255), Math.round(enc[1] * 255), Math.round(enc[2] * 255)];
  }
  var MultiDither = class extends HTMLElement {
    static get observedAttributes() {
      return ["k"];
    }
    connectedCallback() {
      this._mount();
    }
    attributeChangedCallback() {
      if (this._source) this.run();
    }
    _mount() {
      this.innerHTML = `<div class="md-host">
      <div class="md-grid">${ALGOS.map((a) => `
        <div class="md-cell">
          <h4>${a.name}</h4>
          <canvas data-algo="${a.id}" class="md-canvas"></canvas>
        </div>
      `).join("")}</div>
      <p class="md-status" style="color:var(--text-muted);font-size:var(--text-sm);">Drop an image to start.</p>
    </div>`;
      this._status = this.querySelector(".md-status");
    }
    setImage(image) {
      if (!this._status) this._mount();
      const scale = Math.min(1, 280 / Math.max(image.naturalWidth, image.naturalHeight));
      const W = Math.round(image.naturalWidth * scale);
      const H = Math.round(image.naturalHeight * scale);
      const tmp = document.createElement("canvas");
      tmp.width = W;
      tmp.height = H;
      tmp.getContext("2d").drawImage(image, 0, 0, W, H);
      this._source = tmp.getContext("2d").getImageData(0, 0, W, H);
      this._sw = W;
      this._sh = H;
      this.run();
    }
    run() {
      if (!this._source) return;
      const k = Math.max(2, Math.min(16, parseInt(this.getAttribute("k") || "8", 10)));
      this._status.textContent = "Dithering\u2026";
      requestAnimationFrame(() => {
        const t = performance.now();
        const W = this._sw, H = this._sh;
        const data = this._source.data;
        const grid = [];
        const pixels = [];
        for (let y = 0; y < H; y++) {
          const row = [];
          for (let x = 0; x < W; x++) {
            const i = (y * W + x) * 4;
            const r = data[i] / 255, g = data[i + 1] / 255, b = data[i + 2] / 255;
            const lin = decode([r, g, b]);
            const xyz2 = toXYZ5(lin);
            const lab = fromXYZ(xyz2);
            row.push(lab);
            pixels.push(lab);
          }
          grid.push(row);
        }
        const { palette } = quantize(pixels, { k, seed: 42 });
        const paletteBytes = palette.map(oklabToHexBytes2);
        for (const algo of ALGOS) {
          const indices = algo.fn(grid, palette);
          const canv = this.querySelector('canvas[data-algo="' + algo.id + '"]');
          const wCss = Math.min(this.offsetWidth || 360, 380);
          const hCss = Math.round(wCss * H / W);
          const { ctx, w, h } = setupCanvas(canv, wCss, hCss);
          const tmpC = document.createElement("canvas");
          tmpC.width = W;
          tmpC.height = H;
          const imgData = tmpC.getContext("2d").createImageData(W, H);
          for (let y = 0; y < H; y++) {
            for (let x = 0; x < W; x++) {
              const idx = indices[y][x];
              const rgb = paletteBytes[idx];
              const i = (y * W + x) * 4;
              imgData.data[i] = rgb[0];
              imgData.data[i + 1] = rgb[1];
              imgData.data[i + 2] = rgb[2];
              imgData.data[i + 3] = 255;
            }
          }
          tmpC.getContext("2d").putImageData(imgData, 0, 0);
          ctx.imageSmoothingEnabled = false;
          ctx.drawImage(tmpC, 0, 0, w, h);
        }
        const elapsed = (performance.now() - t).toFixed(0);
        this._status.textContent = `${k} colors, ${W}\xD7${H} samples \u2014 4 algorithms in ${elapsed}ms`;
      });
    }
  };
  customElements.define("multi-dither", MultiDither);

  // lib/js/components/image-scatter.js
  var SPECTRAL_LOCUS3 = [
    [0.1741, 5e-3],
    [0.1738, 49e-4],
    [0.1733, 48e-4],
    [0.1726, 48e-4],
    [0.1714, 51e-4],
    [0.1689, 69e-4],
    [0.1644, 0.0109],
    [0.1566, 0.0177],
    [0.144, 0.0297],
    [0.1241, 0.0578],
    [0.0913, 0.1327],
    [0.0454, 0.295],
    [82e-4, 0.5384],
    [0.0139, 0.7502],
    [0.0743, 0.8338],
    [0.1547, 0.8059],
    [0.2296, 0.7543],
    [0.3016, 0.6923],
    [0.3731, 0.6245],
    [0.4441, 0.5547],
    [0.5125, 0.4866],
    [0.5752, 0.4242],
    [0.627, 0.3725],
    [0.6658, 0.334],
    [0.6915, 0.3083],
    [0.7079, 0.292],
    [0.719, 0.2809],
    [0.726, 0.274],
    [0.73, 0.27],
    [0.732, 0.268],
    [0.7334, 0.2666],
    [0.7344, 0.2656],
    [0.7347, 0.2653]
  ];
  var SRGB_TRI = [[0.64, 0.33], [0.3, 0.6], [0.15, 0.06]];
  var P3_TRI = [[0.68, 0.32], [0.265, 0.69], [0.15, 0.06]];
  var REC2020_TRI = [[0.708, 0.292], [0.17, 0.797], [0.131, 0.046]];
  var X_RANGE3 = [0, 0.8];
  var Y_RANGE3 = [0, 0.9];
  var ImageScatter = class extends HTMLElement {
    connectedCallback() {
      this._mount();
    }
    _mount() {
      this.innerHTML = `<div class="scatter-host">
      <canvas class="scatter-canvas"></canvas>
      <div class="scatter-readout" style="color:var(--text-muted);font-size:var(--text-sm);"></div>
    </div>`;
      this._canvas = this.querySelector(".scatter-canvas");
      this._readout = this.querySelector(".scatter-readout");
    }
    setImage(image) {
      if (!this._canvas) this._mount();
      const SAMPLE_TARGET = 160;
      const scale = Math.min(1, SAMPLE_TARGET / Math.max(image.naturalWidth, image.naturalHeight));
      const W = Math.round(image.naturalWidth * scale);
      const H = Math.round(image.naturalHeight * scale);
      const tmp = document.createElement("canvas");
      tmp.width = W;
      tmp.height = H;
      tmp.getContext("2d").drawImage(image, 0, 0, W, H);
      const data = tmp.getContext("2d").getImageData(0, 0, W, H).data;
      this._render(data, W, H);
    }
    _render(data, W, H) {
      const wCss = Math.min(this.offsetWidth || 640, 760);
      const hCss = Math.round(wCss * (Y_RANGE3[1] / X_RANGE3[1]));
      const { ctx, w, h } = setupCanvas(this._canvas, wCss, hCss);
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--bg-card").trim() || "#fff";
      ctx.fillRect(0, 0, w, h);
      const X = (xv) => (xv - X_RANGE3[0]) / (X_RANGE3[1] - X_RANGE3[0]) * w;
      const Y = (yv) => h - (yv - Y_RANGE3[0]) / (Y_RANGE3[1] - Y_RANGE3[0]) * h;
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#888";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      SPECTRAL_LOCUS3.forEach(([x, y], i) => {
        const px = X(x), py = Y(y);
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.closePath();
      ctx.stroke();
      [
        { tri: REC2020_TRI, color: "oklch(0.70 0.18 50 / 0.7)", label: "Rec.2020" },
        { tri: P3_TRI, color: "oklch(0.62 0.18 150 / 0.8)", label: "P3" },
        { tri: SRGB_TRI, color: "oklch(0.55 0.18 264 / 0.9)", label: "sRGB" }
      ].forEach(({ tri, color, label }) => {
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        tri.forEach(([x, y], i) => {
          const px = X(x), py = Y(y);
          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        });
        ctx.closePath();
        ctx.stroke();
      });
      let plotted = 0;
      let inSrgb = 0, inP3 = 0, inRec2020 = 0;
      for (let i = 0; i < data.length; i += 4) {
        const r = data[i] / 255, g = data[i + 1] / 255, b = data[i + 2] / 255;
        const lin = decode([r, g, b]);
        const xyz2 = toXYZ5(lin);
        const sum = xyz2[0] + xyz2[1] + xyz2[2];
        if (sum < 1e-6) continue;
        const xc = xyz2[0] / sum, yc = xyz2[1] / sum;
        const px = X(xc), py = Y(yc);
        if (px < 0 || px > w || py < 0 || py > h) continue;
        const hexR = data[i], hexG = data[i + 1], hexB = data[i + 2];
        ctx.fillStyle = "rgba(" + hexR + "," + hexG + "," + hexB + ",0.7)";
        ctx.fillRect(px - 1, py - 1, 2, 2);
        plotted++;
      }
      this._readout.innerHTML = "<strong>" + plotted + "</strong> pixels plotted on the CIE 1931 xy diagram.";
    }
  };
  customElements.define("image-scatter", ImageScatter);

  // lib/js/components/chip-composer.js
  var ChipComposer = class extends HTMLElement {
    static get observedAttributes() {
      return ["chip-a", "chip-b", "ground-a", "ground-b", "label-a", "label-b", "reveal"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._halvesEl) this.render();
    }
    _mount() {
      this.innerHTML = `
      <div class="cc-host">
        <div class="cc-halves"></div>
        <div class="cc-reveal" hidden>
          <div class="cc-reveal-label">stripped of context:</div>
          <div class="cc-reveal-row">
            <div class="cc-reveal-chip cc-reveal-a"></div>
            <div class="cc-reveal-chip cc-reveal-b"></div>
          </div>
          <div class="cc-reveal-hex"></div>
        </div>
      </div>`;
      this._halvesEl = this.querySelector(".cc-halves");
      this._revealEl = this.querySelector(".cc-reveal");
      this._revealA = this.querySelector(".cc-reveal-a");
      this._revealB = this.querySelector(".cc-reveal-b");
      this._revealH = this.querySelector(".cc-reveal-hex");
    }
    render() {
      const chipA = this.getAttribute("chip-a") || "#888888";
      const chipB = this.getAttribute("chip-b") || "#888888";
      const groundA = this.getAttribute("ground-a") || "#1a1a1a";
      const groundB = this.getAttribute("ground-b") || "#eeeeee";
      const labelA = this.getAttribute("label-a") || "";
      const labelB = this.getAttribute("label-b") || "";
      const reveal = this.getAttribute("reveal") === "true";
      this._halvesEl.innerHTML = `
      <div class="cc-half" style="background:${groundA}">
        <div class="cc-chip" style="background:${chipA}"></div>
        ${labelA ? `<div class="cc-label">${labelA}</div>` : ""}
      </div>
      <div class="cc-half" style="background:${groundB}">
        <div class="cc-chip" style="background:${chipB}"></div>
        ${labelB ? `<div class="cc-label">${labelB}</div>` : ""}
      </div>`;
      this._revealA.style.background = chipA;
      this._revealB.style.background = chipB;
      const same = chipA.toLowerCase() === chipB.toLowerCase();
      this._revealH.innerHTML = same ? `Both chips: <strong>${chipA}</strong> \u2014 physically identical.` : `Left: <strong>${chipA}</strong> \xB7 Right: <strong>${chipB}</strong>`;
      this._revealEl.hidden = !reveal;
    }
  };
  customElements.define("chip-composer", ChipComposer);

  // lib/js/components/homage-canvas.js
  var HomageCanvas = class extends HTMLElement {
    static get observedAttributes() {
      return ["outer", "mid1", "mid2", "inner", "squares"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._frame) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="hc-frame"></div>`;
      this._frame = this.querySelector(".hc-frame");
    }
    render() {
      const outer = this.getAttribute("outer") || "oklch(0.42 0.10 264)";
      const mid1 = this.getAttribute("mid1") || "oklch(0.56 0.13 264)";
      const mid2 = this.getAttribute("mid2") || "oklch(0.72 0.13 264)";
      const inner = this.getAttribute("inner") || "oklch(0.88 0.05 264)";
      const squares = this.getAttribute("squares") === "3" ? 3 : 4;
      const layout4 = [
        { w: 100, t: 0 },
        { w: 78, t: 12 },
        { w: 56, t: 26 },
        { w: 32, t: 44 }
      ];
      const layout3 = [
        { w: 100, t: 0 },
        { w: 70, t: 16 },
        { w: 40, t: 38 }
      ];
      const layout = squares === 4 ? layout4 : layout3;
      const colors = squares === 4 ? [outer, mid1, mid2, inner] : [outer, mid1, inner];
      this._frame.innerHTML = layout.map(
        (L, i) => `<div class="hc-square" style="background:${colors[i]};width:${L.w}%;top:${L.t}%;"></div>`
      ).join("");
    }
  };
  customElements.define("homage-canvas", HomageCanvas);

  // lib/js/components/afterimage-trial.js
  var AfterimageTrial = class extends HTMLElement {
    static get observedAttributes() {
      return ["color", "duration"];
    }
    connectedCallback() {
      this._state = "idle";
      this._mount();
      this._onVisibility = () => {
        if (document.hidden && this._state === "staring") this.reset();
      };
      document.addEventListener("visibilitychange", this._onVisibility);
    }
    _mount() {
      this.innerHTML = `<div class="at-host">
      <div class="at-stage at-stage-idle"></div>
      <div class="at-controls">
        <button class="at-start">start trial</button>
        <button class="at-reset" hidden>reset</button>
      </div>
      <div class="at-instructions"></div>
    </div>`;
      this._stage = this.querySelector(".at-stage");
      this._instructions = this.querySelector(".at-instructions");
      this._startBtn = this.querySelector(".at-start");
      this._resetBtn = this.querySelector(".at-reset");
      this._startBtn.addEventListener("click", () => this.start());
      this._resetBtn.addEventListener("click", () => this.reset());
      this._stage.innerHTML = '<div class="at-fixation" style="color:var(--text-muted)">click <em>start trial</em> to begin</div>';
    }
    start() {
      if (this._state !== "idle") return;
      const color = this.getAttribute("color") || "#cc0033";
      const duration = parseInt(this.getAttribute("duration") || "20", 10);
      this._state = "staring";
      this._startBtn.hidden = true;
      this._stage.classList.remove("at-stage-idle");
      this._stage.style.background = color;
      this._stage.innerHTML = `<div class="at-fixation">+</div><div class="at-countdown">${duration}</div>`;
      let remaining = duration;
      this._interval = setInterval(() => {
        remaining--;
        if (remaining <= 0) {
          clearInterval(this._interval);
          this._stage.style.background = "#ffffff";
          this._stage.innerHTML = '<div class="at-fixation" style="color:#333">+</div><div class="at-reveal-msg">\u2191 stare at the cross \u2014 what color do you see?</div>';
          this._instructions.innerHTML = `You stared at <strong>${color}</strong>. The afterimage you see is its <em>opponent</em>: red \u2192 cyan, blue \u2192 yellow, green \u2192 magenta.`;
          this._resetBtn.hidden = false;
          this._state = "reveal";
        } else {
          const cd = this.querySelector(".at-countdown");
          if (cd) cd.textContent = remaining;
        }
      }, 1e3);
    }
    reset() {
      if (this._interval) clearInterval(this._interval);
      this._state = "idle";
      this._stage.classList.add("at-stage-idle");
      this._stage.style.background = "";
      this._stage.innerHTML = '<div class="at-fixation" style="color:var(--text-muted)">click <em>start trial</em> to begin</div>';
      this._instructions.textContent = "";
      this._startBtn.hidden = false;
      this._resetBtn.hidden = true;
    }
    disconnectedCallback() {
      if (this._interval) clearInterval(this._interval);
      if (this._onVisibility) document.removeEventListener("visibilitychange", this._onVisibility);
    }
  };
  customElements.define("afterimage-trial", AfterimageTrial);

  // lib/js/components/transparency-composer.js
  function fromHex2(hex) {
    hex = hex.replace("#", "");
    return [
      parseInt(hex.slice(0, 2), 16) / 255,
      parseInt(hex.slice(2, 4), 16) / 255,
      parseInt(hex.slice(4, 6), 16) / 255
    ];
  }
  function toHex2(enc) {
    const b = (v) => Math.round(Math.max(0, Math.min(1, v)) * 255).toString(16).padStart(2, "0");
    return "#" + b(enc[0]) + b(enc[1]) + b(enc[2]);
  }
  function oklabMid(aHex, bHex) {
    const aLab = fromXYZ(toXYZ5(decode(fromHex2(aHex))));
    const bLab = fromXYZ(toXYZ5(decode(fromHex2(bHex))));
    const mid = [(aLab[0] + bLab[0]) / 2, (aLab[1] + bLab[1]) / 2, (aLab[2] + bLab[2]) / 2];
    const lin = fromXYZ5(toXYZ(mid));
    return { hex: toHex2(encode([
      Math.max(0, Math.min(1, lin[0])),
      Math.max(0, Math.min(1, lin[1])),
      Math.max(0, Math.min(1, lin[2]))
    ])), lab: mid };
  }
  function rgbMid(aHex, bHex) {
    const a = fromHex2(aHex), b = fromHex2(bHex);
    return toHex2([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2]);
  }
  function deltaE(labA, labB) {
    return Math.sqrt(
      Math.pow(labA[0] - labB[0], 2) + Math.pow(labA[1] - labB[1], 2) + Math.pow(labA[2] - labB[2], 2)
    );
  }
  var TransparencyComposer = class extends HTMLElement {
    static get observedAttributes() {
      return ["color-a", "color-b", "color-c", "auto-mode"];
    }
    connectedCallback() {
      this._mount();
      this.render();
    }
    attributeChangedCallback() {
      if (this._stage) this.render();
    }
    _mount() {
      this.innerHTML = `<div class="tc-host">
      <div class="tc-stage">
        <div class="tc-rect tc-rect-a"></div>
        <div class="tc-rect tc-rect-b"></div>
        <div class="tc-rect tc-rect-c"></div>
      </div>
      <div class="tc-readout"></div>
    </div>`;
      this._stage = this.querySelector(".tc-stage");
      this._rectA = this.querySelector(".tc-rect-a");
      this._rectB = this.querySelector(".tc-rect-b");
      this._rectC = this.querySelector(".tc-rect-c");
      this._readout = this.querySelector(".tc-readout");
    }
    render() {
      const aHex = this.getAttribute("color-a") || "#3366cc";
      const bHex = this.getAttribute("color-b") || "#cc6633";
      const cHexAttr = this.getAttribute("color-c") || "#888888";
      const auto = this.getAttribute("auto-mode") || "none";
      const okMid = oklabMid(aHex, bHex);
      const rgbMidHex = rgbMid(aHex, bHex);
      let actualC = cHexAttr;
      if (auto === "oklab") actualC = okMid.hex;
      else if (auto === "rgb") actualC = rgbMidHex;
      const cLab = fromXYZ(toXYZ5(decode(fromHex2(actualC))));
      const dE = deltaE(cLab, okMid.lab);
      const transparent = dE < 0.04;
      this._rectA.style.background = aHex;
      this._rectB.style.background = bHex;
      this._rectC.style.background = actualC;
      this._readout.innerHTML = `
      <div class="tc-row">A <code>${aHex}</code> \xB7 B <code>${bHex}</code> \xB7 C <code>${actualC}</code></div>
      <div class="tc-row">OKLab midpoint: <code>${okMid.hex}</code> \xB7 RGB midpoint: <code>${rgbMidHex}</code></div>
      <div class="tc-row">\u0394E<sub>ok</sub>(C, OKLab-mid) = <strong>${dE.toFixed(4)}</strong> ${transparent ? '<span class="pill pass">reads as transparent</span>' : '<span class="pill warn">reads as opaque</span>'}</div>`;
    }
  };
  customElements.define("transparency-composer", TransparencyComposer);

  // lib/js/shell.js
  var DEMO_GROUPS = [
    {
      label: "Core color science",
      items: [
        { href: "/examples/pages/picker.html", label: "OKLCh picker" },
        { href: "/examples/pages/okhsl.html", label: "OKHSL picker" },
        { href: "/examples/pages/gradient.html", label: "Gradient comparison" },
        { href: "/examples/pages/blendwhite.html", label: "Blend through white" },
        { href: "/examples/pages/transfer.html", label: "Transfer curves" },
        { href: "/examples/pages/chromaticity.html", label: "CIE xy chromaticity" },
        { href: "/examples/pages/illuminants.html", label: "Spectral illuminants" },
        { href: "/examples/pages/wavelength.html", label: "Wavelength \u2192 color" },
        { href: "/examples/pages/cmf.html", label: "Cone fundamentals" }
      ]
    },
    {
      label: "Gamut & mapping",
      items: [
        { href: "/examples/pages/gamut.html", label: "Gamut envelope" },
        { href: "/examples/pages/mapping.html", label: "Gamut mapping playground" },
        { href: "/examples/pages/wheel.html", label: "Perceptual hue wheel" },
        { href: "/examples/pages/ramp.html", label: "Token ramp generator" },
        { href: "/examples/pages/tonemap.html", label: "HDR tone mapping" },
        { href: "/examples/pages/kelvin.html", label: "Color temperature (Kelvin)" }
      ]
    },
    {
      label: "Accessibility & perception",
      items: [
        { href: "/examples/pages/contrast.html", label: "Contrast (WCAG + APCA)" },
        { href: "/examples/pages/cvd.html", label: "Color-blindness simulator" },
        { href: "/examples/pages/cvdsafe.html", label: "CVD-safe palette" },
        { href: "/examples/pages/deltae.html", label: "\u0394E metric comparator" },
        { href: "/examples/pages/harmony.html", label: "Color harmony generator" },
        { href: "/examples/pages/ciecam16.html", label: "CIECAM16 viewing conditions" },
        { href: "/examples/pages/adapt.html", label: "Chromatic adaptation" }
      ]
    },
    {
      label: "Image analysis",
      items: [
        { href: "/examples/pages/palette.html", label: "Palette extraction" },
        { href: "/examples/pages/imagestats.html", label: "Image color analysis" },
        { href: "/examples/pages/dither.html", label: "Floyd-Steinberg dithering" }
      ]
    },
    {
      label: "Tokens, schemes & CSS",
      items: [
        { href: "/examples/pages/tonal.html", label: "Material 3 tonal palette" },
        { href: "/examples/pages/csscolor5.html", label: "CSS Color 5/6 playground" },
        { href: "/examples/pages/procedural.html", label: "Procedural palettes" },
        { href: "/examples/pages/pigment.html", label: "Kubelka-Munk paint mixer" },
        { href: "/examples/pages/namer.html", label: "Color namer" }
      ]
    },
    {
      label: "Foundations & illusions",
      items: [
        { href: "/examples/pages/macadam.html", label: "MacAdam ellipses" },
        { href: "/examples/pages/illusions.html", label: "Color illusions" },
        { href: "/examples/pages/volume.html", label: "Color volume comparison" },
        { href: "/examples/pages/cube3d.html", label: "3D sRGB cube in OKLab" },
        { href: "/examples/pages/match.html", label: "Color matching game" },
        { href: "/examples/pages/apcatable.html", label: "APCA reading table" },
        { href: "/examples/pages/multidither.html", label: "Multi-dither comparison" },
        { href: "/examples/pages/scatter.html", label: "Image chromaticity scatter" }
      ]
    },
    {
      label: "Josef Albers",
      items: [
        { href: "/examples/pages/albers-who.html", label: "01 \xB7 Who was Josef Albers?" },
        { href: "/examples/pages/albers-relational.html", label: "02 \xB7 Color is relational" },
        { href: "/examples/pages/albers-book.html", label: "03 \xB7 The book as a learning system" },
        { href: "/examples/pages/albers-deception.html", label: "04 \xB7 Color deception" },
        { href: "/examples/pages/albers-simultaneous.html", label: "05 \xB7 Simultaneous contrast" },
        { href: "/examples/pages/albers-one-as-two.html", label: "06 \xB7 One color appearing as two" },
        { href: "/examples/pages/albers-two-as-one.html", label: "07 \xB7 Two colors appearing as one" },
        { href: "/examples/pages/albers-homage.html", label: "08 \xB7 Homage to the Square system" },
        { href: "/examples/pages/albers-square.html", label: "09 \xB7 Why the square?" },
        { href: "/examples/pages/albers-proportion.html", label: "10 \xB7 Proportion, area, weight" },
        { href: "/examples/pages/albers-warm-cool.html", label: "11 \xB7 Temperature is contextual" },
        { href: "/examples/pages/albers-transparency.html", label: "12 \xB7 Transparency illusions" },
        { href: "/examples/pages/albers-afterimage.html", label: "13 \xB7 Afterimage & optical memory" },
        { href: "/examples/pages/albers-vs-science.html", label: "14 \xB7 Albers vs. scientific models" },
        { href: "/examples/pages/albers-digital.html", label: "15 \xB7 Albers for digital design" },
        { href: "/examples/pages/albers-lab.html", label: "16 \xB7 Color lab" }
      ]
    }
  ];
  function resolveHref(rawHref) {
    const path = window.location.pathname;
    const inPages = path.includes("/examples/pages/");
    const inExamplesRoot = path.endsWith("/examples/index.html") || path.endsWith("/examples/");
    if (inPages) {
      if (rawHref === "/examples/index.html") return "../index.html";
      if (rawHref.startsWith("/examples/pages/")) return "./" + rawHref.slice("/examples/pages/".length);
    }
    if (inExamplesRoot) {
      if (rawHref === "/examples/index.html") return "./index.html";
      if (rawHref.startsWith("/examples/pages/")) return "./pages/" + rawHref.slice("/examples/pages/".length);
    }
    return rawHref;
  }
  function currentFilename() {
    return window.location.pathname.split("/").pop() || "index.html";
  }
  function mountSkipLink() {
    const main = document.querySelector(".app-main");
    if (!main || document.querySelector(".skip-link")) return;
    if (!main.id) main.id = "main";
    const link = el("a", { class: "skip-link", href: "#main" }, "skip to content");
    document.body.insertBefore(link, document.body.firstChild);
  }
  function mountHeader() {
    const header = document.querySelector(".app-header");
    if (!header || header.dataset.mounted) return;
    header.dataset.mounted = "1";
    const brandHref = resolveHref("/examples/index.html");
    const here = currentFilename();
    const select = el("select", { class: "app-nav-select", "aria-label": "Jump to demo" });
    const placeholder = el("option", { value: "", disabled: "true" }, "Jump to demo\u2026");
    select.append(placeholder);
    let matchedCurrent = false;
    for (const group of DEMO_GROUPS) {
      const og = el("optgroup", { label: group.label });
      for (const item of group.items) {
        const resolved = resolveHref(item.href);
        const opt = el("option", { value: resolved }, item.label);
        if (resolved.split("/").pop() === here) {
          opt.setAttribute("selected", "true");
          matchedCurrent = true;
        }
        og.append(opt);
      }
      select.append(og);
    }
    if (!matchedCurrent) placeholder.setAttribute("selected", "true");
    select.addEventListener("change", () => {
      if (select.value) window.location.href = select.value;
    });
    const isHome = here === "index.html" || here === "";
    const homeLink = el("a", {
      href: brandHref,
      class: "app-nav-home",
      "aria-current": isHome ? "page" : null
    }, "Home");
    header.innerHTML = "";
    header.append(
      el(
        "a",
        { class: "app-header__brand", href: brandHref },
        el("span", { class: "app-header__brand-dot" }),
        "ref-color ",
        el("small", {}, "examples")
      ),
      el("nav", { class: "app-nav" }, homeLink, select)
    );
  }
  function mountFooter() {
    const footer = document.querySelector(".app-footer");
    if (!footer || footer.dataset.mounted) return;
    footer.dataset.mounted = "1";
    footer.innerHTML = "";
    footer.append(
      el(
        "p",
        {},
        "Static demos dogfooding ",
        el("code", {}, "ref-color"),
        ". Color math: ",
        el("a", { href: "https://bottosson.github.io/posts/oklab/", target: "_blank", rel: "noreferrer" }, "Ottosson 2020"),
        ", ",
        el("a", { href: "https://www.myndex.com/APCA/", target: "_blank", rel: "noreferrer" }, "APCA"),
        ", ",
        el("a", { href: "https://www.w3.org/TR/css-color-4/", target: "_blank", rel: "noreferrer" }, "CSS Color 4"),
        ". No frameworks, no build step at runtime \u2014 just compiled TS modules. ",
        el(
          "span",
          { style: { opacity: "0.7" } },
          "Tip: press ",
          el("kbd", {}, "["),
          " / ",
          el("kbd", {}, "]"),
          " to navigate demos."
        )
      )
    );
  }
  function installKeyNav() {
    const flat2 = [];
    for (const group of DEMO_GROUPS) for (const item of group.items) flat2.push(item.href);
    function isTyping(target) {
      if (!target) return false;
      const tag = target.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return true;
      if (target.isContentEditable) return true;
      return false;
    }
    document.addEventListener("keydown", (e) => {
      if (e.key !== "[" && e.key !== "]") return;
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      if (isTyping(e.target)) return;
      const here = currentFilename();
      let idx = flat2.findIndex((h) => h.split("/").pop() === here);
      let target;
      if (idx === -1) {
        target = e.key === "]" ? flat2[0] : flat2[flat2.length - 1];
      } else {
        const n = flat2.length;
        const next = e.key === "]" ? (idx + 1) % n : (idx - 1 + n) % n;
        target = flat2[next];
      }
      window.location.href = resolveHref(target);
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      mountSkipLink();
      mountHeader();
      mountFooter();
      installKeyNav();
    });
  } else {
    mountSkipLink();
    mountHeader();
    mountFooter();
    installKeyNav();
  }

  // bundle-entry.js
  window.RefColor = {
    // spaces
    oklab: oklab_exports,
    oklch: oklch_exports,
    cielab: cielab_exports,
    cielch: cielch_exports,
    srgb: srgb_exports,
    p3: p3_exports,
    rec2020: rec2020_exports,
    hsl: hsl_exports,
    hsv: hsv_exports,
    hct: hct_exports,
    cam16ucs: cam16_ucs_exports,
    ciecam16: ciecam16_exports,
    jzazbz: jzazbz_exports,
    xyy: xyy_exports,
    xyz: xyz_exports,
    // transfers
    srgbTransfer: srgb_exports2,
    rec2020Transfer: rec2020_exports2,
    pqTransfer: pq_exports,
    hlgTransfer: hlg_exports,
    adobeRgbTransfer: adobe_rgb_exports,
    prophotoTransfer: prophoto_exports,
    // metrics
    luminance: luminance_exports,
    apca: apca_exports,
    deltaE: deltaE_exports,
    // adaptation
    bradford: bradford_exports,
    // cvd
    machado: machado_2009_exports,
    // interpolation
    linearInterp: linear_exports,
    cubehelix: cubehelix_exports,
    lightnessCurves: lightness_curves_exports,
    spline: spline_exports,
    // gamut
    cusp: cusp_exports,
    oklchPeak: oklch_peak_exports,
    mapping: mapping_exports,
    // image processing
    kmeans: kmeans_exports,
    floydSteinberg: floyd_steinberg_exports,
    // foundation
    types: types_exports,
    convert: convert_exports,
    // utility helpers
    utils: utils_exports
  };
})();
