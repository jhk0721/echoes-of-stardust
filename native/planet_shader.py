# 记忆星球 GLSL 渲染器：moderngl 真 shader 优先，纯 Python 翻译兜底
# 算法真源：native/planet.glsl（参考 blackhole.glsl 的噪声/tint/HDR tonemap 风格）
import math
import struct

import pygame

_TEX = 128
_ctx = _prog = _vao = _fbo = None

_VS = """#version 330
in vec2 inPos; out vec2 vUV;
void main(){ vUV = inPos*0.5+0.5; gl_Position = vec4(inPos, 0.0, 1.0); }
"""
_FS = """#version 330
uniform vec3 uBase; uniform float uSeed; uniform vec3 uLight;
in vec2 vUV; out vec4 frag;
float hash21(vec2 p){ p=fract(p*vec2(234.34,435.345)); p+=dot(p,p+34.23); return fract(p.x*p.y); }
float vnoise(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.0-2.0*f);
  return mix(mix(hash21(i),hash21(i+vec2(1.0,0.0)),f.x),
             mix(hash21(i+vec2(0.0,1.0)),hash21(i+vec2(1.0,1.0)),f.x),f.y); }
void main(){
  vec2 uv = vUV*2.0-1.0;
  float d2 = dot(uv,uv);
  vec3 base = uBase/255.0;
  if(d2>1.0){
    float g = max(0.0,1.0-(d2-1.0)/0.9);
    frag = vec4(base*g, 75.0/255.0*g*g);
    return;
  }
  vec3 n = normalize(vec3(uv, sqrt(max(0.0,1.0-d2))));
  float t = hash21(uv*10.0+uSeed);
  vec3 tint = mix(base*vec3(1.15,0.95,0.80), base*vec3(0.85,1.05,1.15), t);
  float bands = vnoise(vec2(uv.x*2.2+uSeed, uv.y*6.0));
  vec3 albedo = tint*(0.75+0.5*bands);
  float dn = dot(n,uLight);
  vec3 col = albedo*(0.12+0.88*max(dn,0.0))*(0.06+0.94*smoothstep(-0.15,0.20,dn));
  float rim = pow(1.0-n.z,2.0);
  col += base*(0.10+rim*0.5);
  col = 1.0-exp(-col*1.6);
  frag = vec4(col,1.0);
}
"""

_LIGHT = (0.45, -0.40, 0.80)
_ll = math.sqrt(sum(v * v for v in _LIGHT))
_LIGHT = tuple(v / _ll for v in _LIGHT)


def _ensure():
    global _ctx, _prog, _vao, _fbo
    if _ctx is not None:
        return True
    try:
        import moderngl
        _ctx = moderngl.create_standalone_context(require=330)
        _prog = _ctx.program(vertex_shader=_VS, fragment_shader=_FS)
        buf = _ctx.buffer(struct.pack("8f", -1, -1, 1, -1, 1, 1, -1, 1))
        _vao = _ctx.vertex_array(_prog, [(buf, "2f", "inPos")])
        _fbo = _ctx.framebuffer(color_attachments=[_ctx.texture((_TEX, _TEX), 4)])
        return True
    except Exception:
        _ctx = None
        return False


def render_glsl(r, col_i, base_col):
    """GLSL 渲染星球纹理（128px 源，缩放到目标尺寸）"""
    if not _ensure():
        return None
    try:
        _prog["uBase"].value = (base_col[0] / 255.0, base_col[1] / 255.0, base_col[2] / 255.0)
        _prog["uSeed"].value = col_i * 31.7 + 7.3
        _prog["uLight"].value = _LIGHT
        _fbo.use()
        _ctx.viewport = (0, 0, _TEX, _TEX)
        _fbo.clear(0.0, 0.0, 0.0, 0.0)
        _vao.render()
        data = _fbo.read(attachment=0, components=4)
        surf = pygame.image.fromstring(data, (_TEX, _TEX), "RGBA")
        surf = pygame.transform.flip(surf, False, True)   # GL 原点左下 → 左上，防暗面跑偏
        w = h = r * 4
        surf = pygame.transform.smoothscale(surf, (w, h))   # 平滑缩放防斜条纹伪影
        return surf.convert_alpha()
    except Exception:
        return None


def _hash21(x, y):
    px, py = math.fmod(x * 234.34, 1.0), math.fmod(y * 435.345, 1.0)
    d = px * px + py * py + 34.23
    return math.fmod((px + d) * (py + d), 1.0)


def _vnoise(x, y):
    ix, fx = math.floor(x), x - math.floor(x)
    iy, fy = math.floor(y), y - math.floor(y)
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    a = _hash21(ix, iy)
    b = _hash21(ix + 1, iy)
    c = _hash21(ix, iy + 1)
    d2 = _hash21(ix + 1, iy + 1)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d2) * fx * fy


def render_python(r, col_i, base):
    """纯 Python 逐像素翻译 planet.glsl（无 GPU 时兜底，结果一致）"""
    b = (base[0] / 255.0, base[1] / 255.0, base[2] / 255.0)   # 归一化，防 tonemap 爆白
    pad = r
    w = h = r * 2 + pad * 2
    S = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = cy = r + pad
    L = _LIGHT
    seed = col_i * 31.7 + 7.3
    for py in range(h):
        for px in range(w):
            dx = (px - cx) / r
            dy = (py - cy) / r
            d2 = dx * dx + dy * dy
            if d2 > 1.0:
                g = max(0.0, 1 - (d2 - 1) / 0.9)
                a = int(75 * g * g)
                if a <= 0:
                    continue
                S.set_at((px, py), (int(base[0] * g), int(base[1] * g),
                                    int(base[2] * g), a))
                continue
            nz = math.sqrt(max(0.0, 1 - d2))
            t = _hash21(int(dx * 10 + seed), int(dy * 10 + seed * 3))
            tint = (b[0] * (1.15 - 0.30 * t), b[1] * (0.95 + 0.10 * t),
                    b[2] * (0.80 + 0.35 * t))
            bands = _vnoise(dx * 2.2 + seed, dy * 6.0)
            fband = 0.75 + 0.5 * bands
            dn = dx * L[0] + dy * L[1] + nz * L[2]
            night = 0.0 if dn < -0.15 else min(1.0, (dn + 0.15) / 0.35) if dn < 0.2 else 1.0
            f = (0.12 + 0.88 * max(dn, 0.0)) * (0.06 + 0.94 * night)
            rim = (1 - nz) ** 2
            col = (1 - math.exp(-(tint[0] * fband * f + b[0] * (0.10 + rim * 0.5)) * 1.6),
                   1 - math.exp(-(tint[1] * fband * f + b[1] * (0.10 + rim * 0.5)) * 1.6),
                   1 - math.exp(-(tint[2] * fband * f + b[2] * (0.10 + rim * 0.5)) * 1.6))
            S.set_at((px, py), (min(255, int(col[0] * 255)), min(255, int(col[1] * 255)),
                                min(255, int(col[2] * 255)), 255))
    return S


def render_any(r, col_i, base_col):
    """GLSL 优先，降级纯 Python"""
    s = render_glsl(r, col_i, base_col)
    if s is None:
        s = render_python(r, col_i, base_col)
    return s
