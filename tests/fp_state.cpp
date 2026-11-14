#include "a64_state.hpp"

int main() {
    A64State state;
    state.x[0] = 1;
    state.x[1] = 0x400000;
    if (run_a64(state, 8) != Status::unsupported_fp_mode ||
        state.x[2] != 1 || state.x[3] != 0x400000 || state.pc != 16)
        return 1;
    state.x[1] = 0;
    return run_a64(state, 8) == Status::returned && state.x[3] == 0 ? 0 : 2;
}
