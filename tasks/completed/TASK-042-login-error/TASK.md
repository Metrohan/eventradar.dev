# TASK-042-login-error: Login error detail'i Türkçe'ye çevir

## Problem

`POST /api/admin/login` başarısız olduğunda dönen `HTTPException.detail` değeri İngilizce'ydi
(`"Invalid username or password"`). Bu, frontend'in toast notification'ı olarak gösterdiği string
olduğundan, TR dilindeki bir UI'da tutarsız görünüyordu.

## Goal

Login endpoint'inin hata mesajı diğer UI stringleriyle tutarlı biçimde Türkçe olmalı.

## Acceptance criteria

- [x] `app/api/admin_auth.py` — `detail` değeri `"Kullanıcı adı veya şifre hatalı"` oldu
- [x] Mevcut test yalnızca 401 status code'u doğruluyor, detail'i değil — test değişikliği gerekmedi

## In scope

- `app/api/admin_auth.py` — tek satır değişiklik

## Out of scope

- Test değişikliği (mevcut test detail'i assert etmiyor)
- Diğer endpoint hata mesajları

## Commit

`4422b38` — `fix(auth): change login error detail to Turkish` — Closes #42
