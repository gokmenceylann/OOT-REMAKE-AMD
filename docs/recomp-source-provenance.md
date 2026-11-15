# Mako 4.1.1 recomp kaynak kaydı

| Bileşen | Kimlik | Bu dalda kullanım |
| --- | --- | --- |
| OOT-REMAKE-AMD kararlı tabanı | v0.1.5 — 93e7586cf57f65260b4bab3cde1eecb3d28573bc | Dalın başlangıcı |
| Mako 4.1.1 gitlink | b77ac86187330eb7447ac65ab23187baac4600ca | Runtime, lifter ve renderer kaynağı |
| İlk yerel derleme | mako-4.1.1 (source f1566ec9), shader stamp fe6b0a1d7ec998de | Regresyon referansı |
| İncelenen Longshot HEAD | fa2cc03aa5c2369dea53856d4b11bdb9d0299b3b | Kaynak karşılaştırması |
| Longshot HEAD ebeveyni | 9447e1de5e01ffab15a179ab4b55a1320fe14231 | Git ata kontrolüne göre Mako tabanında mevcut |

Windows x64 baseline runtime SHA-256 değerleri:

~~~text
55398f7d9ff34698d01bd249be26e45f79d6dc635d21438cbece6c46788dafac  hookshot.exe
d21fbd99e39c87781f86980795d8fbf840ac2fe3bc34a5b1c1f5c432aa1b8cd2  hookshot_vk.dll
~~~

Ana kaynak Mako 4.1.1'dir. Mako geçmişindeki `3eba32ec`,
`5d648794` ve `95161232`, ortak Hookshot/Longshot işlerinin
hangi yoldan geldiğini gösterir. İncelenen Longshot HEAD renderer
API 14, Mako ise API 23 kullanır. ABI eşleşmesi build
doğrulamasının parçasıdır. Mevcut FSR 4.1.2 yaması, FSR 3.1
fallback ve Radeon bellek yaması bu tabandan gelir.

### Longshot'tan gelen upstream işler

| SHA | Alan | Durum |
| --- | --- | --- |
| `16c42ef06c` | Background iş hatası sonucunu yayımlama, `vk_jobs.cpp` | Mako geçmişinde mevcut |
| `39d978b49f` | AMD ASTC/resolve, `vk_vma.cpp` | Mako geçmişinde mevcut |
| `325583b981` | Vulkan import/bind hata geri dönüşü, `vk_memory.cpp` | Mako geçmişinde mevcut |
| `2982420d3f`, `8fc2587c7d`, `0cf9936c01` | FSR uniform, image retirement ve temporal history | Mako geçmişinde mevcut |
| `5e4e2113d8` | Upstream pipeline state listesi | Commit geçmişte mevcut. Yerel listenin içeriği ayrıca doğrulanmalı. |

Bu dalda Longshot'tan doğrudan alınan kod, patch veya hazır
derleme yok. Gelecekteki her aktarım için upstream URL ve tam SHA,
dosya/fonksiyon, alınan ya da uyarlanan kapsam, lisans, yerel commit,
cache damgası ve test kanıtı kaydedilir. Oyundan veya kullanıcı
dosyalarından türetilen çıktılar depoya eklenmez.

- [OOT kararlı etiket](https://github.com/gokmenceylann/OOT-REMAKE-AMD/tree/v0.1.5)
- [Mako 4.1.1 kaynağı](https://github.com/Shakoquo/Mako/tree/b77ac86187330eb7447ac65ab23187baac4600ca)
- [İncelenen Longshot kaynağı](https://github.com/Recomper/Longshot/tree/fa2cc03aa5c2369dea53856d4b11bdb9d0299b3b)
