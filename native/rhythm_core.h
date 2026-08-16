#ifndef RHYTHM_CORE_H
#define RHYTHM_CORE_H

#ifdef _WIN32
  #define API __declspec(dllexport)
#else
  #define API
#endif

extern "C" {
    /* 单步判定：note=玩家音符(0-3), expected=期望音符, dt_ms=距上一拍时间,
       gap_ms=拍间隔, win_ms=判定窗口
       返回: 0=太早忽略, 1=命中, 2=错过 */
    API int step(int note, int expected, float dt_ms, float gap_ms, float win_ms);

    /* 批量判定：返回命中数（目标与按键一一对应） */
    API int judge_sequence(const int* target, const int* presses,
                           const float* times, int n, float gap_ms, float win_ms);
}

#endif
