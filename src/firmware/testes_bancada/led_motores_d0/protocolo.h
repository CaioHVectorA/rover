#pragma once
#include "rover_protocolo.h"

namespace TesteD0 {
constexpr unsigned long BAUD = 9600;
constexpr int PWM = 120;             // Mesmo valor bruto do teste direto confirmado.
constexpr uint32_t PULSO_MS = 1000;
constexpr uint32_t PAUSA_MS = 150;   // Saidas desligadas antes de qualquer novo pulso.

inline bool valido(const ProtoFrame &f) {
  switch (f.cmd) {
    case 'L': return f.n == 1 && f.arg[0] >= 0 && f.arg[0] <= 2;
    case 'M': return f.n == 2 && f.arg[0] >= -PWM && f.arg[0] <= PWM
                            && f.arg[1] >= -PWM && f.arg[1] <= PWM;
    case 'X': return f.n == 0;
    default: return false;
  }
}
}  // namespace TesteD0
