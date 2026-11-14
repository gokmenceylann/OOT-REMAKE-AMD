#include "horizon_services.hpp"

int main() {
    A64State missing;
    if (run_a64(missing, 16) != Status::unsupported_service ||
        missing.last_service != horizon::get_system_tick || missing.x[1] != 0) return 1;
    A64State guest;
    guest.service_handler = horizon::dispatch;
    if (run_a64(guest, 16) != Status::guest_exit || guest.last_service != horizon::exit_process ||
        guest.x[1] != 9 || guest.x[3] != guest.x[0]) return 2;
    const auto previous = guest.x[0];
    return guest.invoke_service(horizon::get_system_tick) == ServiceResult::resume &&
           guest.x[0] >= previous && guest.invoke_service(0xffff) == ServiceResult::unsupported ? 0 : 3;
}
