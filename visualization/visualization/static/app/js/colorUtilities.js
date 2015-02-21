/* accepts parameters
 * h  Object = {h:x, s:y, v:z}
 * OR
 * h, s, v
*/
function HSVtoRGB(h, s, v) {
    var r, g, b, i, f, p, q, t;
    if (h && s === undefined && v === undefined) {
        s = h.s, v = h.v, h = h.h;
    }
    i = Math.floor(h * 6);
    f = h * 6 - i;
    p = v * (1 - s);
    q = v * (1 - f * s);
    t = v * (1 - (1 - f) * s);
    switch (i % 6) {
        case 0: r = v, g = t, b = p; break;
        case 1: r = q, g = v, b = p; break;
        case 2: r = p, g = v, b = t; break;
        case 3: r = p, g = q, b = v; break;
        case 4: r = t, g = p, b = v; break;
        case 5: r = v, g = p, b = q; break;
    }
    return {
        r: Math.floor(r * 255),
        g: Math.floor(g * 255),
        b: Math.floor(b * 255)
    };
}

function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(color) {
    return "#" + componentToHex(color.r) + componentToHex(color.g) + componentToHex(color.b);
}

function LogScaler(values) {
    var minval = Math.min.apply(null, values);
    var maxval = Math.max.apply(null, values);
    var log = Math.log10
    var A = log(maxval - minval + 1);
    var b = minval;

    var scale = function(x) {
        return log(x - b + 1)/A;
    };

    return scale;
}
function LinearScaler(values) {
    var minval = Math.min.apply(null, values);
    var maxval = Math.max.apply(null, values);

    var A = maxval - minval;
    var b = minval;

    var scale = function(x) {
        return (x - b)/A;
    };

    return scale;
}

function RedGreenColorMapper(values, Scaler){
    var scale = Scaler(values);

    return function(n){
        var h = (1-scale(n))/3;
        var s = 1;
        var v = 1;
        color = rgbToHex(HSVtoRGB(h,s,v));
        return color;
    };
}