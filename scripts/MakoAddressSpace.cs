using System;
using System.Runtime.InteropServices;

public static class MakoAddressSpace {
    [StructLayout(LayoutKind.Sequential)]
    private struct Region {
        public UIntPtr BaseAddress;
        public UIntPtr AllocationBase;
        public uint AllocationProtect;
        public ushort PartitionId;
        public UIntPtr RegionSize;
        public uint State;
        public uint Protect;
        public uint Type;
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr OpenProcess(uint access, bool inherit, int pid);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern UIntPtr VirtualQueryEx(IntPtr process, UIntPtr address, out Region info, UIntPtr length);
    [DllImport("kernel32.dll")]
    private static extern bool CloseHandle(IntPtr process);

    public static ulong[] Query(int pid) {
        // Mako 4.1.1: A64_HOST_BASE in a64.h and HOS_GUEST_SPACE in hos.h.
        const ulong guestStart = 0x100000000000;
        const ulong guestEnd = guestStart + (1UL << 39);
        const uint commit = 0x1000, privateType = 0x20000, mapped = 0x40000, image = 0x1000000;
        IntPtr process = OpenProcess(0x0400, false, pid);
        if (process == IntPtr.Zero) throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
        try {
            var sums = new ulong[4];
            bool sawGuest = false;
            ulong address = 0;
            var size = (UIntPtr)(uint)Marshal.SizeOf(typeof(Region));
            while (true) {
                if (VirtualQueryEx(process, (UIntPtr)address, out Region info, size) != size) {
                    const int invalidParameter = 87; // Address above the accessible range.
                    int error = Marshal.GetLastWin32Error();
                    if (error != invalidParameter) throw new System.ComponentModel.Win32Exception(error);
                    break;
                }
                ulong start = info.BaseAddress.ToUInt64();
                ulong end = start + info.RegionSize.ToUInt64();
                if (end <= address) throw new InvalidOperationException("Invalid virtual region size");
                if (info.AllocationBase.ToUInt64() == guestStart) sawGuest = true;
                if (info.State == commit) {
                    ulong guest = Math.Min(end, guestEnd) > Math.Max(start, guestStart)
                        ? Math.Min(end, guestEnd) - Math.Max(start, guestStart) : 0;
                    sums[0] += guest;
                    ulong outside = end - start - guest;
                    if (info.Type == privateType) sums[1] += outside;
                    if (info.Type == mapped) sums[2] += outside;
                    if (info.Type == image) sums[3] += outside;
                }
                address = end;
            }
            if (!sawGuest) throw new InvalidOperationException("The Mako 4.1.1 guest reservation was not found.");
            return sums;
        } finally {
            CloseHandle(process);
        }
    }
}
