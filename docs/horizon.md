# Horizon SVC

Derlenen `svc #imm` çağrıları A64State servis işleyicisine iletilir. `horizon::dispatch` ile `0x1e` monoton 19,2 MHz test sayacı döndürür ve `0x07` yalnızca misafir yürütümünü bitirir. Kayıtlı olmayan çağrı, kimliği kaydedilerek unsupported_service ile durur. Sayaç başlangıcı host sürecine özeldir.

SVC numaraları için [libnx svc.s](https://github.com/switchbrew/libnx/blob/master/nx/source/kernel/svc.s) referans alındı. Thread, bellek yönetimi, dosya sistemi ve IPC henüz yok. Bu işleyici sentetik fixture ile doğrulandı. Oyun başlangıç yoluna bağlanmadı.
