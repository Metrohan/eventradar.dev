# Hukuki metin taslakları (YAYINLANMADI)

Bu klasördeki üç metin **taslaktır**; Site'de yayınlanmamış, hiçbir rotaya bağlanmamıştır. Hukuki görüş değildir. Yayınlamadan önce bir avukata gösterilmelidir.

| Dosya | Amaç |
|---|---|
| `aydinlatma-metni.md` | KVKK m.10 aydınlatma yükümlülüğü |
| `gizlilik-politikasi.md` | Ziyaretçiye yönelik sade özet |
| `kullanim-kosullari.md` | Kullanım koşulları (ToS) |

## Kodda doğrulanan dayanaklar (2026-10-22)

- IP: `AnalyticsService.log_request` son oktedi sıfırlar (IPv6 için /48), `traffic_logs` 90 gün sonra silinir (`app/services/analytics_service.py`).
- İstek sınırlama IP'yi yalnızca süreç belleğinde tutar (`app/services/rate_limiter.py`).
- Çerez yok: `app/` ve `frontend/nginx.conf` içinde `Set-Cookie` bulunmadı. Tarayıcı depolaması: `eventradar:lang`, `eventradar:favorites`, `eventradar:filters`, `theme` (`admin_token` yalnızca yönetici girişinde).
- İzleme betiği yok (gtag, analytics, piksel bulunmadı). Üçüncü taraf istekleri: Google Fonts, jsDelivr, cdnjs (`frontend/index.html`).
- E-bülten çift onaylı; abonelikten çıkış satırı **siler** (`app/api/public.py`). Push iptali de satırı siler.
- Etkinlik talebi formu da aynı şekilde (e-posta adresi dahil) site sahibine iletilir.
- Öneri/şikayet formu kaydedilir **ve** `FEEDBACK_NOTIFY_EMAIL` adresine e-postayla iletilir (arka planda, e-posta sağlayıcısı üzerinden).
- Formlar: öneri/şikayet (tür, başlık, metin), etkinlik talebi (bağlantı, başlık, tarih, açıklama, isteğe bağlı e-posta).

## Doldurulması gereken alanlar (`[DOLDURULACAK]`)

Veri sorumlusunun adı/unvanı, adresi ve iletişim e-postası; yürürlük tarihi; barındırma ve e-posta sağlayıcısı ve konumları; sunucu erişim kaydı saklama süresi; ToS'ta yetkili il ve içerik/lisans sahibi. Bunlar kodda yok, uydurulmadı.

## Yayınlamadan önce verilmesi gereken kararlar

1. **Öneri/şikayet ve etkinlik talebi saklama süresi:** Kodda otomatik silme yok; bu kayıtlar şu an süresiz tutuluyor. Süre belirleyin ve silme mekanizması ekleyin (talep edilirse yapılabilir).
2. **Onaylanmamış abonelikler:** `confirmed=False` kayıtlar hiç silinmiyor (süre sınırı yok). Bir temizleme süresi belirleyin.
3. **Sunucu erişim kayıtları:** Host nginx tam IP'leri yazıyor olabilir. Saklama süresini ve yasal dayanağı (5651 kapsamında yer sağlayıcı sayılıp sayılmadığınızı) avukatla netleştirin; `sudo` gerektirdiği için log yapılandırması incelenmedi.
4. **Yurt dışı aktarım (KVKK m.9):** Google Fonts ve CDN'ler tarayıcıyı doğrudan yurt dışına bağlar. Alternatif: bu dosyaları kendi sunucunuzdan sunmak (aktarımı ortadan kaldırır; talep edilirse yapılabilir).
5. **E-bülten ve ticari ileti:** Bülten içeriğinin 6563 sayılı Kanun kapsamında "ticari elektronik ileti" sayılıp sayılmadığını ve gerekli izin/İYS yükümlülüğünü kontrol edin.
6. **VERBİS** kayıt yükümlülüğünün sizin için geçerli olup olmadığını kontrol edin.
7. **Doğrulanmadı:** "Veriler sunucuda sınırlı erişimle tutulur" gibi güvenlik cümleleri genel ifadedir; gerçek durumla eşleştiğini siz teyit edin. Host nginx'in çerez set etmediği de doğrulanmadı (yalnızca uygulama ve frontend nginx tarandı).

## Yayınlama (yapılmadı)

Sitede şu an ilgili rota yok (`frontend/src/App.jsx`). Yayınlamak için sayfalar, rotalar, altbilgi bağlantıları ve (varsa) abonelik/talep formlarına onay metni bağlantısı eklenmelidir. Bu, kamuya açık bir değişikliktir ve ayrıca onayınızı gerektirir.
