#pragma once
#include "a64_state.hpp"
#include <chrono>

namespace horizon {
inline constexpr std::uint16_t exit_process = 0x07;
inline constexpr std::uint16_t get_system_tick = 0x1e;
inline constexpr std::uint64_t ticks_per_second = 19'200'000;

inline ServiceResult dispatch(A64State& state, std::uint16_t service) {
    if (service == exit_process) return ServiceResult::exit_process;
    if (service == get_system_tick) {
        using TickDuration = std::chrono::duration<std::uint64_t, std::ratio<1, ticks_per_second>>;
        static const auto epoch = std::chrono::steady_clock::now();
        state.x[0] = std::chrono::duration_cast<TickDuration>(
            std::chrono::steady_clock::now() - epoch).count();
        return ServiceResult::resume;
    }
    return ServiceResult::unsupported;
}
}
