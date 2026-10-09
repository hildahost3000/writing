// Vercel function: /api/sync. The logic is in _core.js; this file only connects it to Vercel Blob.
import { get, put } from '@vercel/blob';
import { handle } from './_core.js';

const store = {
  async get(pathname) {
    const r = await get(pathname, { access: 'private', useCache: false });   // useCache:false = never a stale copy
    if (!r || r.statusCode !== 200) return null;
    return { etag: r.blob.etag, text: await new Response(r.stream).text() };
  },
  async put(pathname, text, { ifMatch } = {}) {
    const blob = await put(pathname, text, {
      access: 'private',
      contentType: 'application/json',
      allowOverwrite: Boolean(ifMatch),     // creating must not clobber an existing document
      ...(ifMatch ? { ifMatch } : {}),
      cacheControlMaxAge: 60,
    });
    return { etag: blob.etag };
  },
};

export default async function handler(req, res) {
  let body;
  if (req.method === 'PUT') {
    body = req.body;
    if (typeof body === 'string') { try { body = JSON.parse(body); } catch { body = null; } }
  }
  const out = await handle({ method: req.method, authorization: req.headers.authorization, body }, store);
  res.status(out.status);
  for (const [k, v] of Object.entries(out.headers)) res.setHeader(k, v);
  res.send(out.body);
}
