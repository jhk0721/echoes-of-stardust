// planet.glsl —— 记忆星球着色器（参考 blackhole.glsl 的噪声/tint/HDR 风格）
// 本项目 pygame 无 shader 管线，此文件为算法真源，运行时由
// core/main.py::render_planet_glsl 用纯 Python 逐像素翻译执行（结果一致）。

float hash21(vec2 p) {
    p = fract(p * vec2(234.34, 435.345));
    p += dot(p, p + 34.23);
    return fract(p.x * p.y);
}

// value noise：x 低频（色带）、y 高频（气态条纹）
float vnoise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i),          hash21(i + vec2(1, 0)), f.x),
               mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), f.x), f.y);
}

vec3 planet(vec2 uv, vec3 base, float seed, vec3 lightDir) {
    vec3 n = normalize(vec3(uv, sqrt(max(0.0, 1.0 - dot(uv, uv)))));  // 球面法线
    // 冷暖 tint（blackhole 风格）
    vec3 warm = base * vec3(1.15, 0.95, 0.80);
    vec3 cool = base * vec3(0.85, 1.05, 1.15);
    vec3 tint = mix(warm, cool, hash21(uv * 10.0 + seed));
    // 条纹反照率
    float bands = vnoise(vec2(uv.x * 2.2 + seed, uv.y * 6.0));
    vec3 albedo = tint * (0.75 + 0.5 * bands);
    // 统一光源（左上）：漫反射 + 夜面
    float diff = max(dot(n, lightDir), 0.0);
    float night = smoothstep(-0.15, 0.20, dot(n, lightDir));
    vec3 col = albedo * (0.20 + 0.80 * diff) * (0.15 + 0.85 * night);
    // 边缘大气光晕
    float rim = pow(1.0 - n.z, 2.0);
    col += base * rim * 0.55;
    // HDR tonemap（黑洞吸积盘同款曝光曲线）
    col = 1.0 - exp(-col * 1.5);
    return col;
}
