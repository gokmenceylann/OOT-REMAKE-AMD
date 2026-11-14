#pragma once
#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

enum class Status { returned, fell_through, memory_fault, bad_return, budget_exhausted, external_branch };

struct A64State {
    static constexpr std::uint64_t return_to_host = UINT64_MAX;
    std::array<std::uint64_t, 32> x{};  // Slot 31 is SP. XZR is handled by the compiler.
    bool n{}, z{}, c{}, v{};
    std::uint64_t pc{}, stop_target{};
    std::uint64_t memory_base{};
    std::span<std::uint8_t> memory;

    A64State() { x[30] = return_to_host; }

    void set_flags(std::uint64_t a, std::uint64_t b, std::uint64_t r, unsigned width, char op) {
        const auto sign = std::uint64_t{1} << (width - 1);
        n = (r & sign) != 0;
        z = r == 0;
        c = op == '+' ? r < a : op == '-' && a >= b;
        v = op == '+' ? ((~(a ^ b) & (a ^ r)) & sign) != 0 :
            op == '-' && (((a ^ b) & (a ^ r)) & sign) != 0;
    }

    bool contains(std::uint64_t address, std::size_t size) const {
        return address >= memory_base && address - memory_base <= memory.size() &&
            size <= memory.size() - (address - memory_base);
    }

    bool fill(std::uint64_t address, std::uint64_t value, std::size_t size) {
        if (!contains(address, size)) return false;
        if (size) std::fill_n(memory.data() + (address - memory_base), size, std::uint8_t(value));
        return true;
    }

    bool load(std::uint64_t address, std::size_t size, std::uint64_t& value) const {
        if (size > 8 || !contains(address, size)) return false;
        value = 0;
        for (std::size_t i = 0; i < size; ++i)
            value |= std::uint64_t(memory[address - memory_base + i]) << (8 * i);
        return true;
    }

    bool store(std::uint64_t address, std::size_t size, std::uint64_t value) {
        if (size > 8 || !contains(address, size)) return false;
        for (std::size_t i = 0; i < size; ++i)
            memory[address - memory_base + i] = std::uint8_t(value >> (8 * i));
        return true;
    }
};

Status run_a64(A64State& s, std::uint64_t budget,
               std::uint64_t return_address = A64State::return_to_host);
