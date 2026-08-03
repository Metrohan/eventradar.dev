# TASK-023-channels: Kullanıcı hesapları yerine kanal keşif UI'ı

## Problem

Issue #23 "user accounts" özelliği planlanmıştı. Ancak kullanıcı, projenin iletişim
kanallarının email + Telegram + RSS olduğunu ve hesap sistemi yerine bu kanalları
kullanıcılara gösterecek UI indikatörlerinin daha uygun olduğuna karar verdi.

## Kullanıcı Kararı

- Issue #23 (user accounts) → **wontfix** olarak kapatıldı
- Yerine: Kullanıcıları üç mevcut kanala (email, Telegram, RSS) yönlendiren UI bileşeni

## Acceptance criteria

- [x] `ChannelsBanner.jsx` — üç interaktif kart (Email, Telegram, RSS) ile yeni component
- [x] `HomePage.jsx` — `<ChannelsBanner />` EventListing'in altına eklendi
- [x] `Footer.jsx` — `id="footer-subscribe"` anchor eklendi (email kartının scroll hedefi)
- [x] `Footer.jsx` — Telegram ikonu sosyal linkler arasına eklendi
- [x] `tr/common.json` ve `en/common.json` — `channelsBanner.*` ve `footer.telegramAria` key'leri eklendi

## Teknik Detaylar

- Email kartı: `#footer-subscribe` anchor'a scroll (sayfa içi)
- Telegram: `https://t.me/eventradar_tr` (external, `_blank`)
- RSS: `/api/events/rss` (external, `_blank`)
- Hover efekti için `colorHex` ayrı string değişkeni — CSS var ile box-shadow içindeki string interpolation uyumsuzluğundan dolayı

## Commit

`570f04a` — `feat(ui): add channel discovery banner and Telegram footer link`

## Wontfix Kararları (aynı oturumda)

Aynı issue triage oturumunda wontfix olarak kapatılan diğer issue'lar (kod değişikliği yok):
- #29, #30, #31, #32 — uluslararası kapsam özellikleri (proje Türkiye-yerel kalacak)
- #23 — kullanıcı hesapları (bu task'ın yerini aldı)
- #20 — past event auto-archive (zaten uygulanmış, kod değişikliği gerekmedi)
- #77 — mobile FCP/LCP (zaten PR #87 ile çözülmüş)
- #76 — oversized images (zaten uygulanmış image_pipeline.py ile)
