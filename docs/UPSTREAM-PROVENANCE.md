# Upstream kaynak kökeni

## Sabitlenen geliştirme tabanı

| Öğe | Doğrulanan kimlik |
| --- | --- |
| Yeni geliştirme dalı | `mako-4.1.1-longshot` |
| İlk commit ve OOT v0.1.5 etiketi | `93e7586cf57f65260b4bab3cde1eecb3d28573bc` |
| Mako 4.1.1 gitlink | `b77ac86187330eb7447ac65ab23187baac4600ca` |
| İlk yerel derleme | `mako-4.1.1 (source f1566ec9)`, shader stamp `fe6b0a1d7ec998de` |
| İncelenen Longshot main | `fa2cc03aa5c2369dea53856d4b11bdb9d0299b3b` |
| Karşılaştırılan OOT main | `54d06dfc6a4ffdd5e05c47ef60ae8ada53d7a947` |

Yerel Windows x64 runtime SHA-256 değerleri v0.1.5
manifestiyle eşleşti.

~~~text
55398f7d9ff34698d01bd249be26e45f79d6dc635d21438cbece6c46788dafac  hookshot.exe
d21fbd99e39c87781f86980795d8fbf840ac2fe3bc34a5b1c1f5c432aa1b8cd2  hookshot_vk.dll
~~~

`f1566ec9`, kaynak içeriği parmak izidir. Sürüm kökenini
gitlink ve build loguyla, ikili kimliğini SHA-256 ile izliyoruz.

## Kaynak ağacı

~~~text
Hookshot ortak kaynak geçmişi
├─ Recomper/Longshot 9447e1de… → fa2cc03a… (Longshot adı)
└─ Mako / Hookshot uyarlaması
   ├─ 3eba32ec: yeniden adlandırma öncesi işler
   ├─ 5d648794 ve 95161232: sonraki işler, Hookshot adları korunarak
   ├─ 22b8d22d: late pages ve sparse mirror için Mako varsayılanları
   └─ b77ac861…: Mako 4.1.1 / renderer API 23
      └─ OOT 93e7586… / v0.1.5
         └─ mako-4.1.1-longshot (belge ve hazırlık dalı)
~~~

Longshot HEAD'in ebeveyni
`9447e1de5e01ffab15a179ab4b55a1320fe14231` için
`git merge-base --is-ancestor` Mako tabanında başarı verdi.
`fa2cc03a` yeniden adlandırma commit'idir. İncelenen
`Recomper/Longshot` ağacında renderer API 14, Mako 4.1.1'de 23.
Mako commit açıklamasındaki API 22 atfı, güncel
`Recomper/Longshot` snapshot'ının ABI değeri olarak kullanılamaz.

## v0.1.5 ve main farkı

v0.1.5 `Build-LocalGame.ps1` boş yama listesiyle başlar.
`-EnableFsr412` FSR yamasını, `-EnableMemoryOptimization`
Radeon bellek yamasını ekler. Kılavuzdaki AMD derleme komutu
ikisini açar. Standalone builder, yerel ExeFS/RomFS üzerinden
`hookshot.exe`, `hookshot_vk.dll` ve oyun imajını oluşturur.
Başlangıç shader hazırlığı build komutunda
`--no-prepare-shaders` ile ertelenir.

Karşılaştırılan main aynı Mako gitlink'ini kullanıyor ve
şu renderer yamalarını build'e varsayılan ekliyor:

| Commit | Yama | Kapsam |
| --- | --- | --- |
| `19a79e2` | `fg-present-recovery.patch` | Windows deferred FG batch acquire için 20 ms sınır |
| `fe126c1` | `pipeline-performance.patch` | Cache yazım alanı denetimi ve strict AMD cache-only probe |
| `7ca5904` | `fg-incomplete-frame.patch` | Eksik kareleri FG history dışında tutma |
| `489be27` | `pipeline-slow-key.patch` | Tam pipeline anahtarı, VkResult ve compile feedback |
| `76fe7d3` | `pipeline-recent-warmup.patch` | İsteğe bağlı son kullanılan pipeline hazırlığı ve probe opt-in |
| `3d3e838` | `pipeline-region-warmup.patch` | İsteğe bağlı bölge profili |
| `d2a5d22` | `pipeline-region-use.patch` | Graphics/compute kullanım profili ve açılışta tekrar kullanma |

`03c94b5` performans audit yamasını ayrı switch ile ekler.
Sonraki ön yayın ve importer commit'leri dağıtım yolunu değiştirir.
Bu yamalar yeni dalın kaynak tabanına alınmadı. v0.1.5 etiketi
ve main geçmişi yerinde kalır.

## Aktarım kaydı

İncelenen Longshot deposunda yayımlanmış GitHub Release veya
Git etiketi yoktu. Builder ve release workflow kaynakları
bulunuyor. Doğrulanmış bir Longshot release binary'si,
sürümü veya dosya konumu kaydedilecek durumda değil.
Yeni dalda alınan Longshot dosyası, patch veya hazır ikili yok.

İleride her aktarım için upstream repo ve tam SHA, kaynak
sürüm veya ref, dosya ve fonksiyon, alınan veya uyarlanan
kapsam, lisans bildirimi, yerel commit, ABI/cache damgası,
test sonucu ve ikili varsa SHA-256 yazılır.

- [OOT v0.1.5 kaynağı](https://github.com/gokmenceylann/OOT-REMAKE-AMD/tree/v0.1.5)
- [Mako merge commit'i](https://github.com/Shakoquo/Mako/commit/95161232165bf8646e178a1db62170c9d2743fa2)
- [Sabit Mako ağacı](https://github.com/Shakoquo/Mako/tree/b77ac86187330eb7447ac65ab23187baac4600ca)
- [Longshot HEAD](https://github.com/Recomper/Longshot/commit/fa2cc03aa5c2369dea53856d4b11bdb9d0299b3b)
- [Longshot Releases](https://github.com/Recomper/Longshot/releases)
