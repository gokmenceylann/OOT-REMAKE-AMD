#include "a64_state.hpp"
int main() {
    std::array<std::uint8_t, 32> ram{};
    const auto fresh = [&]() {
        A64State state;
        state.memory = ram;
        state.memory_base = 0x2000;
        state.x[31] = 0x2010;
        state.x[1] = 0x2010;
        return state;
    };
    auto call = fresh();
    call.x[0] = 0xffffffff00000103ULL;
    if (run_a64(call, 64) != Status::returned || call.x[0] != 3 || ram[16] != 2 || !call.c || call.z)
        return 1;
    auto branch = fresh();
    branch.x[0] = 1;
    if (run_a64(branch, 64) != Status::returned || branch.x[0] != 42 || !branch.z)
        return 2;
    auto fault = fresh();
    fault.x[31] = 0x2008;
    if (run_a64(fault, 64) != Status::memory_fault || run_a64(branch, 0) != Status::budget_exhausted)
        return 3;
    auto bad = fresh();
    bad.x[0] = 1;
    bad.x[30] = 0x123;
    if (run_a64(bad, 64) != Status::bad_return) return 4;
    auto overflow = fresh();
    overflow.x[0] = 0x80000000;
    if (run_a64(overflow, 64) != Status::returned || !overflow.v || overflow.n || !overflow.c)
        return 5;
}
