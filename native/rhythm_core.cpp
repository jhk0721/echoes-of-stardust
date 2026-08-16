// rhythm_core.cpp —— 织曲系统判定核心（C++ 20% 部分）
// 与 Python 侧 native/bridge.py 的 _py_step 保持同构，保证降级路径行为一致
#include "rhythm_core.h"

extern "C" {

int step(int note, int expected, float dt_ms, float gap_ms, float win_ms) {
    if (dt_ms < gap_ms - win_ms) return 0;                    // 太早，忽略
    if (dt_ms <= gap_ms + win_ms) return (note == expected) ? 1 : 2;
    return 2;                                                 // 超窗，算错过
}

int judge_sequence(const int* target, const int* presses,
                   const float* times, int n, float gap_ms, float win_ms) {
    int hits = 0;
    int idx = 0;
    float last = -1e9f;
    for (int i = 0; i < n; i++) {
        if (last < 0.0f) {
            last = times[i];
            hits += (presses[i] == target[idx]) ? 1 : 0;
            idx++;
            continue;
        }
        float dt = times[i] - last;
        if (dt < gap_ms - win_ms) continue;                   // 太早的按键不算新拍
        last = times[i];
        if (idx < n && presses[i] == target[idx] && dt <= gap_ms + win_ms) hits++;
        idx++;
    }
    return hits;
}

}
