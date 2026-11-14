# OOT Remake AMD

Bağımsız Windows x64 statik port araştırması. İlk aşama, önceden ayrıştırılmış ExeFS dizinindeki NSO0 modüllerinin temel segment sınırlarını denetler. Python 3.10 veya üzeri gerekir.

```powershell
python inspect_exefs.py 'C:\Games\OOT\exefs'
python -m unittest -v
```

Araç kaynak oyun dosyalarına yazmaz ve yalnızca başlık metadatasını raporlar. Ek araç, düz veya LZ4 sıkıştırmalı segmentleri bellekte açıp sağlanan SHA-256 değerlerini denetler. ZBIC, relocation, AArch64 çevirisi, Horizon servisleri ve NVN2 çizimi bu sürümün kapsamında değildir. **Bu sürüm Zelda'yı başlatmaz.** Depo Nintendo içeriği veya anahtarı içermez.

[NSO başlık referansı](https://github.com/switchbrew/switch-tools/blob/master/src/elf2nso.c)

```powershell
python -m pip install -r requirements.txt
python verify_exefs.py 'C:\Games\OOT\exefs'
python -m unittest -v
```

## Modül eşleme

```powershell
python map_exefs.py 'C:\Games\OOT\exefs'
```

Araç doğrulanmış NSO segmentlerini ve sıfır dolgulu BSS'yi belleğe eşler. Sembol gerektirmeyen AArch64 RELA ve sıkıştırılmış RELR relocation kayıtlarını uygular. ABS64, GLOB_DAT ve JUMP_SLOT girdilerini ayrı sayar. Kaynak dosyalara yazmaz ve eşlenen görüntüyü dışarı aktarmaz. Bu komut bir modül denetimidir. Oyun yürütme ortamı henüz yoktur.
