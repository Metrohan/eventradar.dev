# Kategori / Tag Sistemi — Tasarım Dokümanı

**Tarih:** 2026-05-25  
**Durum:** Onaylandı  
**Kapsam:** Backend model + scraper sınıflandırma + API filtresi + Frontend badge UI

---

## Genel Bakış

Eventradar'daki etkinliklere otomatik olarak kategori etiketleri (tag) atanacak. Scraper'lar etkinliği kaydederken başlık ve açıklama üzerinde anahtar kelime eşleştirmesi yaparak kategori(ler)i belirleyecek. Kullanıcılar ana sayfada renkli badge'lere tıklayarak kategoriye göre filtreleme yapabilecek.

---

## 1. Veri Modeli

### Yeni tablolar

**`tags`**
```
id     INTEGER PRIMARY KEY
name   VARCHAR(50) UNIQUE NOT NULL   -- slug: "hackathon", "seminer", "atolye", ...
label  VARCHAR(50) NOT NULL          -- görünen ad: "Hackathon", "Seminer / Webinar", ...
color  VARCHAR(20) NOT NULL          -- CSS renk adı: "blue", "purple", "green", ...
```

**`event_tags`** (ara tablo, many-to-many)
```
event_id  INTEGER FK → events.id  ON DELETE CASCADE
tag_id    INTEGER FK → tags.id    ON DELETE CASCADE
PRIMARY KEY (event_id, tag_id)
```

### `Event` modeline eklenen ilişki

```python
event_tags = Table(
    "event_tags",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id", ondelete="CASCADE")),
    Column("tag_id",   Integer, ForeignKey("tags.id",   ondelete="CASCADE")),
    PrimaryKeyConstraint("event_id", "tag_id"),
)

class Event(Base):
    ...
    tags = relationship("Tag", secondary=event_tags, lazy="selectin")
```

`lazy="selectin"` kullanımı N+1 sorgusunu önler; mevcut `get_events()` çağrısı tek sorguda kalır.

### Seed verisi (6 tag)

| name       | label              | color  |
|------------|--------------------|--------|
| hackathon  | Hackathon          | blue   |
| seminer    | Seminer / Webinar  | purple |
| atolye     | Atölye             | green  |
| konferans  | Konferans          | orange |
| bootcamp   | Bootcamp           | pink   |
| diger      | Diğer              | gray   |

---

## 2. Anahtar Kelime Sınıflandırma Motoru

**Dosya:** `app/services/tag_service.py`

```python
KEYWORD_MAP = {
    "hackathon": ["hackathon", "hack", "datathon", "ideathon"],
    "seminer":   ["seminer", "webinar", "sunum", "söyleşi", "konuşma"],
    "atolye":    ["atölye", "workshop", "lab", "pratik", "uygulama"],
    "konferans": ["konferans", "summit", "zirve", "conference"],
    "bootcamp":  ["bootcamp", "boot camp", "yoğun eğitim", "kamp"],
}
```

**`classify_event(title: str, description: str | None) -> list[str]`**

1. `title + " " + (description or "")` birleştirilip küçük harfe çevrilir.
2. Her kategori için KEYWORD_MAP listesi aranır; eşleşen tüm kategori name'leri toplanır.
3. Hiç eşleşme yoksa `["diger"]` döndürülür.

**Entegrasyon noktası:** `app/services/scraper_service.py` → `process_scraped_events()` içinde event DB'ye yazılırken `classify_event()` çağrılır ve dönen tag name'leri `event.tags` ilişkisine atanır.

**Backfill:** Mevcut etkinlikleri etiketlemek için `scripts/backfill_tags.py` tek seferlik çalıştırılır.

---

## 3. API Değişiklikleri

### Schema

`app/schemas/event.py` → `EventResponse`:
```python
tags: list[str] = []   # tag name'leri: ["hackathon", "atolye"]
```

### Endpoint

`GET /api/events` — yeni opsiyonel query parametresi:
```
GET /api/events?tags=hackathon&tags=atolye
```

FastAPI'de `tags: list[str] = Query(default=None)` olarak tanımlanır; tekrarlayan parametre sözdizimi kullanılır (virgülle ayrılmış tek string değil). Frontend axios çağrısı `params: { tags: selectedTags }` ile bunu otomatik üretir.

- Filtre mantığı: **OR** — seçilen kategorilerden en az birini taşıyan etkinlikler döner.
- `tags` parametresi verilmezse davranış değişmez (geriye dönük uyumlu).

### Servis

`app/services/event_service.py` → `get_events()`:
```python
def get_events(self, active_only=True, tags: list[str] | None = None):
    query = self.db.query(Event)
    if active_only:
        query = query.filter(Event.is_active == True)
    if tags:
        query = query.filter(Event.tags.any(Tag.name.in_(tags)))
    return query.order_by(Event.date).all()
```

**Admin endpoint:** Bu aşamada eklenmez. Tag atama otomatiktir; admin paneline tag düzenleme eklenmez.

---

## 4. Frontend

### Renk paleti (CSS custom properties)

```css
/* tag-renkleri */
--tag-hackathon-bg:   rgba(56, 189, 248, 0.15);
--tag-hackathon-text: #38bdf8;
--tag-hackathon-border: rgba(56, 189, 248, 0.5);

--tag-seminer-bg:   rgba(168, 85, 247, 0.15);
--tag-seminer-text: #a855f7;
--tag-seminer-border: rgba(168, 85, 247, 0.5);

--tag-atolye-bg:   rgba(34, 197, 94, 0.15);
--tag-atolye-text: #22c55e;
--tag-atolye-border: rgba(34, 197, 94, 0.5);

--tag-konferans-bg:   rgba(251, 146, 60, 0.15);
--tag-konferans-text: #fb923c;
--tag-konferans-border: rgba(251, 146, 60, 0.5);

--tag-bootcamp-bg:   rgba(244, 63, 94, 0.15);
--tag-bootcamp-text: #f43f5e;
--tag-bootcamp-border: rgba(244, 63, 94, 0.5);

--tag-diger-bg:   rgba(148, 163, 184, 0.15);
--tag-diger-text: #94a3b8;
--tag-diger-border: rgba(148, 163, 184, 0.4);
```

### Tag renk haritası (frontend sabiti)

`TagBadge` renk bilgisini API'dan değil, frontend'deki sabit bir haritadan alır. 6 kategori sabittir, API response'ta sadece `name` slug'ı taşınır.

```js
// frontend/src/components/TagBadge.jsx içinde
const TAG_STYLES = {
  hackathon: { label: 'Hackathon',         emoji: '🏆', color: 'blue'   },
  seminer:   { label: 'Seminer / Webinar',  emoji: '🎓', color: 'purple' },
  atolye:    { label: 'Atölye',             emoji: '🛠', color: 'green'  },
  konferans: { label: 'Konferans',          emoji: '🎤', color: 'orange' },
  bootcamp:  { label: 'Bootcamp',           emoji: '💻', color: 'pink'   },
  diger:     { label: 'Diğer',              emoji: '📌', color: 'gray'   },
}
```

### Yeni bileşen: `TagBadge`

`frontend/src/components/TagBadge.jsx` — tek bir tag'i görselleştiren küçük bileşen. `name` prop'u alır, `TAG_STYLES`'dan renk/label/emoji çeker. Hem kart üzerinde hem filtre satırında kullanılır.

### `HomePage.jsx` değişiklikleri

- `selectedTags: string[]` state eklenir (çoklu seçim).
- Filtre satırına mevcut Platform/Konum dropdown'larının **altına** yeni bir badge satırı eklenir.
- Seçilen badge'ler vurgulanır (outline → filled arka plan); ikinci tıklama seçimi kaldırır.
- `filteredEvents` hesaplaması: `selectedTags` boşsa filtre yok; doluysa OR mantığıyla eşleşen etkinlikler gösterilir.
- `hasFilters` ve "Temizle" butonu `selectedTags`'i de kapsar.

### `EventCard.jsx` değişiklikleri

- Kaynak badge'inin yanına etkinliğin tag'leri `<TagBadge>` olarak eklenir.
- Birden fazla tag varsa hepsi gösterilir (max 2 önerilir, taşarsa `+N` gösterimi).

---

## 5. Veritabanı Migrasyonu

```bash
alembic revision --autogenerate -m "add tags many-to-many"
alembic upgrade head
```

Seed verisi: `app/services/tag_service.py` içinde `seed_tags(db)` fonksiyonu; `app/main.py` startup hook'unda çağrılır (idempotent — tekrar çalışırsa duplicate oluşturmaz).

---

## 6. Test Kapsamı

- `tests/unit/test_tag_service.py` — `classify_event()` için birim testler (her kategoriden en az 1 pozitif, 1 negatif vaka)
- `tests/integration/test_api_public.py` — `?tags=` filtresi için entegrasyon testi

---

## Kapsam Dışı (Bu Fazda)

- Admin panelinden manuel tag düzenleme
- Yeni kategori ekleme arayüzü
- Tag bazlı istatistik sayfası
- SEO / SSR değişiklikleri
