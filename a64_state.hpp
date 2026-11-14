#pragma once
#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

enum class Status { returned, fell_through, memory_fault, bad_return, budget_exhausted, external_branch, guest_exit, unsupported_service, unsupported_fp_mode };
enum class ServiceResult { resume, exit_process, unsupported };

struct A64State {
    static constexpr std::uint64_t return_to_host = UINT64_MAX;
    std::array<std::uint64_t, 32> x{};  // Slot 31 is SP. XZR is handled by the compiler.
    std::array<std::array<std::uint64_t, 2>, 32> q{};
    std::uint32_t fpcr{}, fpsr{};
    bool n{}, z{}, c{}, v{};
    std::uint64_t pc{}, stop_target{};
    std::uint64_t memory_base{};
    std::span<std::uint8_t> memory;

    // Registered guest addresses are data. Never cast a guest value to a host function pointer.
    using HostRoutine = std::uint64_t (*)(std::uint64_t, std::uint64_t, std::uint64_t, std::uint64_t);
    struct HostBinding { std::uint64_t guest; HostRoutine routine; };
    std::span<const HostBinding> bindings;

    bool invoke_host(std::uint64_t target) {
        for (const auto& binding : bindings) {
            if (binding.guest == target && binding.routine) {
                x[0] = binding.routine(x[0], x[1], x[2], x[3]);
                return true;
            }
        }
        return false;
    }

    using ServiceHandler = ServiceResult (*)(A64State&, std::uint16_t);
    ServiceHandler service_handler = nullptr;
    std::uint16_t last_service{};

    ServiceResult invoke_service(std::uint16_t service) {
        last_service = service;
        return service_handler ? service_handler(*this, service) : ServiceResult::unsupported;
    }

    A64State() { x[30] = return_to_host; }

    void set_flags(std::uint64_t a, std::uint64_t b, std::uint64_t r, unsigned width, char op) {
        const auto sign = std::uint64_t{1} << (width - 1);
        n = (r & sign) != 0;
        z = r == 0;
        c = op == '+' ? r < a : op == '-' && a >= b;
        v = op == '+' ? ((~(a ^ b) & (a ^ r)) & sign) != 0 :
            op == '-' && (((a ^ b) & (a ^ r)) & sign) != 0;
    }

    template<unsigned Width>
    static constexpr std::uint64_t lane_mask = UINT64_MAX >> (64 - Width);

    template<unsigned Width>
    static std::uint64_t read_lane(const std::array<std::uint64_t, 2>& value, unsigned lane) {
        const unsigned bit = Width * lane;
        return (value[bit / 64] >> (bit % 64)) & lane_mask<Width>;
    }

    template<unsigned Width>
    static void write_lane(std::array<std::uint64_t, 2>& target, unsigned lane, std::uint64_t value) {
        const unsigned bit = Width * lane;
        const unsigned shift = bit % 64;
        target[bit / 64] = (target[bit / 64] & ~(lane_mask<Width> << shift)) |
                           ((value & lane_mask<Width>) << shift);
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
