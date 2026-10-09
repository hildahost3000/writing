// Sync API logic, kept independent of Vercel so it can be tested with an in-memory store.
//
// One JSON document per sync code. The code is never stored: the document lives at sync/<sha256(code)>.json,
// so without the code there's no way to find it. Writes are conditional on the document's ETag, so two devices
// can never silently overwrite each other (the loser gets a 409 and re-merges).

const MAX_BODY = 600_000;     // bytes of JSON accepted
const MAX_POINTS = 600;       // grammar points in a document
const MAX_TEXT = 20_000;      // characters of sentences per point
const MAX_DAYS = 1500;
const MAX_REVIEWS = 300;      // teacher corrections per grammar point

const HEADERS = {
  'Content-Type': 'application/json; charset=utf-8',
  'Cache-Control': 'no-store',
  'X-Content-Type-Options': 'nosniff',
};

export const normalizeCode = c => String(c || '').replace(/[\s-]/g, '').toUpperCase();
const CODE_RE = /^[A-Z2-7]{26,64}$/;      // long enough that it can't be guessed

async function pathFor(code) {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode('n2-grammar-sync:' + code));
  return 'sync/' + [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('') + '.json';
}

const isObj = v => v && typeof v === 'object' && !Array.isArray(v);

// Rebuild the document from known fields only, so nothing unexpected is ever stored.
export function sanitize(doc) {
  if (!isObj(doc) || !isObj(doc.texts)) return null;
  const texts = {};
  for (const [id, p] of Object.entries(doc.texts)) {
    if (!/^\d{1,4}$/.test(id) || !isObj(p) || typeof p.t !== 'string' || !Number.isFinite(p.u)) return null;
    if (p.t.length > MAX_TEXT) return null;
    texts[id] = { t: p.t, u: Math.trunc(p.u) };
  }
  if (Object.keys(texts).length > MAX_POINTS) return null;
  const days = {};
  if (doc.days !== undefined) {
    if (!isObj(doc.days) || Object.keys(doc.days).length > MAX_DAYS) return null;
    for (const [day, perDevice] of Object.entries(doc.days)) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(day) || !isObj(perDevice) || Object.keys(perDevice).length > 20) return null;
      days[day] = {};
      for (const [dev, n] of Object.entries(perDevice)) {
        if (!/^[A-Za-z0-9]{1,16}$/.test(dev) || !Number.isFinite(n) || n < 0) return null;
        days[day][dev] = Math.trunc(n);
      }
    }
  }
  const out = { v: 1, texts, days };
  if (doc.reviews !== undefined) {
    const reviews = sanitizeReviews(doc.reviews);
    if (!reviews) return null;
    out.reviews = reviews;
  }
  return out;
}

// Teacher corrections: { "<grammar id>": [ { s: sentence as written, c: correction, n: note, v: 'ok'|'fix', done, gone, at } ] }
export function sanitizeReviews(reviews) {
  if (!isObj(reviews) || Object.keys(reviews).length > MAX_POINTS) return null;
  const out = {};
  for (const [id, list] of Object.entries(reviews)) {
    if (!/^\d{1,4}$/.test(id) || !Array.isArray(list) || list.length > MAX_REVIEWS) return null;
    out[id] = [];
    for (const it of list) {
      if (!isObj(it) || typeof it.s !== 'string' || it.s.length > 600 || !(it.v === 'ok' || it.v === 'fix') || !Number.isFinite(it.at)) return null;
      const c = it.c ?? '', n = it.n ?? '';
      if (typeof c !== 'string' || c.length > 600 || typeof n !== 'string' || n.length > 2000) return null;
      out[id].push({ s: it.s, c, n, v: it.v, done: Boolean(it.done), gone: Boolean(it.gone), at: Math.trunc(it.at) });
    }
  }
  return out;
}

const isConflict = e => e?.name === 'BlobPreconditionFailedError' || /already exists|precondition/i.test(e?.message || '');

// request: { method, authorization, body }.  store: { get(path) -> {etag, text}|null, put(path, text, {ifMatch}) -> {etag} }
export async function handle({ method, authorization, body }, store) {
  const reply = (status, obj) => ({ status, headers: HEADERS, body: JSON.stringify(obj) });

  // No code: just tell the page that sync exists on this site.
  if (method === 'GET' && !authorization) return reply(200, { ok: true, sync: 1 });

  const m = /^Bearer\s+(.+)$/i.exec(authorization || '');
  const code = m && normalizeCode(m[1]);
  if (!code || !CODE_RE.test(code)) return reply(401, { error: 'bad sync code' });
  const path = await pathFor(code);

  try {
    if (method === 'GET') {
      const r = await store.get(path);
      return reply(200, r ? { etag: r.etag, doc: JSON.parse(r.text) } : { etag: null, doc: null });
    }
    if (method === 'PUT') {
      if (!isObj(body) || JSON.stringify(body).length > MAX_BODY) return reply(413, { error: 'too large' });
      const doc = sanitize(body.doc);
      if (!doc) return reply(400, { error: 'invalid document' });
      if (body.etag != null && typeof body.etag !== 'string') return reply(400, { error: 'invalid etag' });
      // An older copy of the page doesn't know about corrections and would upload a document without them. Keep the stored ones.
      if (doc.reviews === undefined && body.etag) {
        const cur = await store.get(path);
        const kept = cur && JSON.parse(cur.text).reviews;
        if (kept) doc.reviews = kept;
      }
      try {
        const r = await store.put(path, JSON.stringify(doc), body.etag ? { ifMatch: body.etag } : {});
        return reply(200, { etag: r.etag });
      } catch (e) {
        if (isConflict(e)) return reply(409, { conflict: true });
        throw e;
      }
    }
    return reply(405, { error: 'method not allowed' });
  } catch (e) {
    console.error('sync error:', e?.name, e?.message);   // never log the code
    return reply(500, { error: 'storage error' });
  }
}
