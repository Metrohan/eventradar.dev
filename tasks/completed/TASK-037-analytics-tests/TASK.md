# TASK-037-analytics-tests: AnalyticsService get_stats edge case testleri

## Problem

`AnalyticsService.get_stats()` için iki kenar durum test edilmemişti:
1. `today_visitors` sayacı dünkü kayıtları dışarıda tutmalı
2. Eşit request sayısına sahip iki yol `top_pages`'de ikisi birden görünmeli

## Goal

`tests/unit/test_analytics_service.py` dosyasına bu iki senaryoyu kapsayan testler eklenmeli.

## Acceptance criteria

- [x] `test_today_visitors_excludes_yesterday` — dünkü timestamp'li log'lar `today_visitors`'ı etkilemiyor
- [x] `test_top_pages_tie_both_paths_present` — eşit sayılı iki path her ikisi de sonuçta görünüyor

## Dikkat

Sıra asıl edilmedi — tie-break sırası DB implementasyonuna özgü (SQLite vs PostgreSQL farklı davranabilir).
Her path için count değeri assert edildi, sıra assert edilmedi.

## Commit

`7aa75f8` — `test(analytics): add edge case coverage for get_stats` — Closes #37
