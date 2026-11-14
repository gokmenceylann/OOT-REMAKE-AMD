#include "a64_state.hpp"
#include <array>

static std::uint64_t host_add(std::uint64_t a, std::uint64_t b, std::uint64_t c, std::uint64_t d) {
    return a + 2 * b + 3 * c + 4 * d;
}

int main() {
    A64State s;
    const std::array bindings{A64State::HostBinding{0x9000, host_add}};
    s.bindings = bindings;
    s.x[0] = 1;
    s.x[1] = 2;
    s.x[2] = 3;
    s.x[3] = 4;
    return run_a64(s, 32) == Status::returned && s.x[0] == 30 &&
           !s.invoke_host(0x9001) ? 0 : 1;
}
