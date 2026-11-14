# OOT Remake AMD

Bağımsız Windows x64 statik port araştırması. İlk aşama, önceden ayrıştırılmış ExeFS dizinindeki NSO0 modüllerinin temel segment sınırlarını denetler. Python 3.10 veya üzeri gerekir.

```powershell
python inspect_exefs.py 'C:\Games\OOT\exefs'
python -m unittest -v
```

Araç kaynak oyun dosyalarına yazmaz ve yalnızca başlık metadatasını raporlar. Segment hash doğrulaması, açma, relocation, AArch64 çevirisi, Horizon servisleri ve NVN2 çizimi bu sürümün kapsamında değildir. **Bu sürüm Zelda'yı başlatmaz.** Depo Nintendo içeriği veya anahtarı içermez.

[NSO başlık referansı](https://github.com/switchbrew/switch-tools/blob/master/src/elf2nso.c)
