# TESTS — TASK-028-i18n-close

## Otomasyon

```bash
# JSON geçerliliği
python3 -c "import json; json.load(open('frontend/src/i18n/locales/tr/common.json'))" && echo "TR OK"
python3 -c "import json; json.load(open('frontend/src/i18n/locales/en/common.json'))" && echo "EN OK"
```

## Manuel Testler (implementasyon sonrası)

| # | Adım | Beklenen Sonuç | Durum |
|---|---|---|---|
| 1 | TR dilinde ThemeToggle üzerine hover | Tooltip: "Açık Mod'a Geç" (dark modda) / "Koyu Mod'a Geç" (light modda) | ⬜ |
| 2 | EN'e geç, hover | Tooltip: "Switch to Light Mode" / "Switch to Dark Mode" | ⬜ |
| 3 | DevTools > Elements > ThemeToggle button | `aria-label` attribute görünmeli | ⬜ |
| 4 | Dil değiştir → tooltip reactif güncellenir | Hover sonrası yeni dil metni | ⬜ |
| 5 | Browser console | i18n missing key uyarısı yok | ⬜ |

## Henüz Çalıştırılmayan Testler

- Unit test (bileşen için test dosyası mevcut değil)
- E2E (Playwright konfigürasyonu mevcut değil)
