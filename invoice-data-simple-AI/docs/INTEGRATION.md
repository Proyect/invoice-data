Integración con tu sistema actual

Frontend (React)
- En `src/frontend/src/services/api.ts`, agrega un cliente para `/infer` (o usa fetch directo):
```ts
export async function inferInvoice(file: File, documentType: 'invoice'|'dni_front'|'dni_back' = 'invoice') {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch('http://localhost:8010/infer?document_type=' + documentType, { method: 'POST', body: form });
  if (!res.ok) throw new Error('Inferencia falló');
  return res.json();
}
```
- Consumir `fields` y `detections` en la UI. Los `fields` pueden alimentar tus formularios actuales.

Backend (FastAPI existente)
- Crear un endpoint proxy para mantener autenticación/DB:
```python
@router.post('/documents/extract')
async def extract_document(file: UploadFile = File(...), document_type: str = 'invoice', current_user: User = Depends(get_current_user)):
    infer_url = 'http://rtdetr_api:8010/infer'  # o http://localhost:8010/infer en dev local
    async with httpx.AsyncClient(timeout=60) as client:
        form = {'document_type': document_type}
        files = {'file': (file.filename, await file.read(), file.content_type)}
        r = await client.post(infer_url, params=form, files=files)
        r.raise_for_status()
        data = r.json()
    # persistir si se requiere: guardar detections/fields en tu modelo
    return data
```

Docker Compose conjunto
- Añade el servicio `rtdetr_api` a tu compose y conéctalo a la misma red.
- El backend podrá llamarlo por nombre de servicio (`http://rtdetr_api:8010`).

Seguridad
- Protege `/infer` detrás de tu backend si necesitas control de acceso/auditoría.

