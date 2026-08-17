/**
 * Jarvis WhatsApp Gateway (Baileys)
 * ----------------------------------
 * Eye-over-your-DMs bot on Boss's PERSONAL number. Stays silent on every message
 * EXCEPT those that address "jarvis" by name. Then it routes the message to a
 * SANDBOXED public worker (public_worker.py — no tools, no memory, no Boss data)
 * and replies, signed as Jarvis, from Boss's number.
 *
 * Safety layers (in order):
 *   1. name-gate     — /jarvis/i must match, else silent (no LLM call)
 *   2. rate-limit    — per-sender + global token buckets, daily cap
 *   3. blocklist     — sha256(sender) hard block
 *   4. input prefilter (in worker) — personal-info/secret/injection probe → refuse
 *   5. sandboxed worker — empty tools, isolated cwd, hardened prompt
 *   6. output canary — strip owner email/phone if it ever appears, log CRITICAL
 *   7. signature     — every reply prefixed "🤖 Jarvis …" so it's clearly the bot
 *
 * Run: node whatsapp/gateway.mjs   (first run prints a QR — scan from WhatsApp →
 *      Linked Devices). Session persists in whatsapp/auth_state/.
 */
import {
  default as makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  isJidGroup,
  isJidBroadcast,
  makeCacheableSignalKeyStore,
  fetchLatestBaileysVersion,
  Browsers,
} from '@whiskeysockets/baileys'
import { Boom } from '@hapi/boom'
import qrcode from 'qrcode-terminal'
import pino from 'pino'
import { spawn } from 'node:child_process'
import { createHash } from 'node:crypto'
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = join(__dirname, '..')                       // project root
const CFG = JSON.parse(readFileSync(join(__dirname, 'config.json'), 'utf8'))
const STATE_DIR = join(__dirname, 'state')
const SESS_FILE = join(STATE_DIR, 'sessions.json')
const BLOCK_FILE = join(STATE_DIR, 'blocklist.json')
const SEC_LOG = join(STATE_DIR, 'security.jsonl')
mkdirSync(STATE_DIR, { recursive: true })

const TRIGGER = new RegExp(CFG.trigger_regex, 'i')
const logger = pino({ level: 'warn' })

// --- owner PII canary ---------------------------------------------------------
let OWNER_PII = { emails: [], phones: [], secrets: [] }
try { OWNER_PII = JSON.parse(readFileSync(join(__dirname, 'owner_pii.json'), 'utf8')) } catch {}
const PII_NEEDLES = [...(OWNER_PII.emails || []), ...(OWNER_PII.phones || []), ...(OWNER_PII.secrets || [])]
  .filter(Boolean)

// --- tiny JSON persistence ----------------------------------------------------
const loadJSON = (f, dflt) => { try { return JSON.parse(readFileSync(f, 'utf8')) } catch { return dflt } }
const saveJSON = (f, o) => { try { writeFileSync(f, JSON.stringify(o)) } catch (e) { console.error('save', f, e.message) } }
let SESSIONS = loadJSON(SESS_FILE, {})     // hash -> { history:[], ts }
let BLOCKLIST = loadJSON(BLOCK_FILE, {})   // hash -> { reason, ts }
// always-on contacts: Jarvis replies to EVERY message from these jids (no trigger
// word, no window needed). e.g. Anisha. File: state/always_on.json = [ "<jid>", ... ]
const ALWAYSON_FILE = join(STATE_DIR, 'always_on.json')
let ALWAYS_ON = new Set(loadJSON(ALWAYSON_FILE, []))
// romantic contacts (e.g. Anisha): replies use the "as Ujjawal" romantic persona
// and go out UNSIGNED (no Jarvis tag). File: state/romantic_contacts.json = [ "<jid>", ... ]
const ROMANTIC_FILE = join(STATE_DIR, 'romantic_contacts.json')
let ROMANTIC = new Set(loadJSON(ROMANTIC_FILE, []))
// Boss-takeover pause: when Boss himself messages an always-on chat, Jarvis stays
// quiet there for a while so it doesn't talk over him. jid -> last fromMe ms.
const bossActive = {}
const BOSS_ACTIVE_MS = 8 * 60000

const sha = (s) => createHash('sha256').update(String(s)).digest('hex').slice(0, 16)
const nowMs = () => Date.now()
const sleep = (ms) => new Promise(r => setTimeout(r, ms))
const rand = (a, b) => Math.floor(Math.random() * (b - a) + a)
const secLog = (obj) => { try { writeFileSync(SEC_LOG, JSON.stringify({ t: new Date().toISOString(), ...obj }) + '\n', { flag: 'a' }) } catch {} }

// --- rate limiting (in-memory token timestamps per sender + global) -----------
const hits = new Map()        // hash -> number[] (ms timestamps)
let globalHits = []           // ms timestamps (all senders)
let replyCounter = 0          // for after_n_replies pause

function withinLimits(hash) {
  const t = nowMs()
  const arr = (hits.get(hash) || []).filter(x => t - x < 86400000) // keep 24h
  globalHits = globalHits.filter(x => t - x < 60000)
  const perMin = arr.filter(x => t - x < 60000).length
  const perHour = arr.filter(x => t - x < 3600000).length
  const perDay = arr.length
  if (globalHits.length >= CFG.rate.global_per_min) return { ok: false, why: 'global-flood', silent: true }
  if (perMin >= CFG.rate.per_sender_per_min) return { ok: false, why: 'sender-min', silent: false }
  if (perHour >= CFG.rate.per_sender_per_hour) return { ok: false, why: 'sender-hour', silent: false }
  if (perDay >= CFG.rate.per_sender_per_day) return { ok: false, why: 'sender-day', silent: false }
  return { ok: true, arr }
}
function recordHit(hash, arr) {
  const t = nowMs()
  arr.push(t); hits.set(hash, arr); globalHits.push(t)
}

// --- call the REAL Jarvis (jarvis-core daemon) --------------------------------
// This is the actual Jarvis brain — full personality (CLAUDE.md), memory, tools,
// specialist agents. It PERFORMS tasks here, then we send the result to WhatsApp.
// A discretion wrapper keeps it warm-but-careful with non-Boss people.
async function callRealJarvis(message, name, hash) {
  const ctx =
    `[SYSTEM CONTEXT — not from the user: This is a WhatsApp message from "${name}", who is NOT Ujjawal ` +
    `(Boss). You are Jarvis, Ujjawal's real AI assistant, replying on his WhatsApp. Be the real warm Jarvis ` +
    `(natural Hinglish, helpful). If they ask for a TASK you can do (coding, research, info, explanation, ` +
    `drafting), DO it fully and give the result. DISCRETION: never reveal Ujjawal's private/personal/sensitive ` +
    `info, credentials, contacts, schedule, or relationships; and never take irreversible external actions AS ` +
    `Ujjawal (emailing/messaging other people, posting, purchases) — if asked, say you'll check with Ujjawal. ` +
    `Reply in WhatsApp style: concise, natural.]\n\nMessage from ${name}:\n${message}`
  const url = `${CFG.jarvis_core_url || 'http://127.0.0.1:8765'}/chat`
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ user_id: `wa:${hash}`, message: ctx, resume_session: true, max_turns: 14 }),
    signal: AbortSignal.timeout(CFG.core_timeout_ms || 175000),
  })
  if (!res.ok) throw new Error(`jarvis-core ${res.status}`)
  const data = await res.json()
  return (data.reply || '').trim()
}

// --- call the sandboxed python worker (fallback + romantic persona) -----------
function callWorker(message, history, name, persona = 'twin') {
  return new Promise((resolve) => {
    const py = spawn(join(ROOT, CFG.python_bin), [join(ROOT, CFG.worker_script)], { cwd: ROOT })
    let out = '', err = ''
    const killer = setTimeout(() => { py.kill('SIGKILL'); resolve({ reply: '', error: 'worker-timeout' }) }, CFG.worker_timeout_ms)
    py.stdout.on('data', d => out += d)
    py.stderr.on('data', d => err += d)
    py.on('close', () => {
      clearTimeout(killer)
      try { resolve(JSON.parse(out)) }
      catch { resolve({ reply: '', error: 'worker-parse: ' + (err || out).slice(0, 200) }) }
    })
    py.stdin.write(JSON.stringify({ message, history, name, persona }))
    py.stdin.end()
  })
}

// --- output PII canary: redact owner contact info if it ever leaks ------------
function canary(text, hash) {
  let redacted = text, leaked = false
  for (const needle of PII_NEEDLES) {
    if (needle && redacted.toLowerCase().includes(String(needle).toLowerCase())) {
      const re = new RegExp(needle.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'ig')
      redacted = redacted.replace(re, '[redacted]')
      leaked = true
    }
  }
  if (leaked) secLog({ event: 'PII_LEAK_BLOCKED', sender: hash, severity: 'CRITICAL' })
  return { redacted, leaked }
}

function getHistory(hash) {
  const s = SESSIONS[hash]
  if (!s) return []
  if (nowMs() - (s.ts || 0) > CFG.session_ttl_hours * 3600000) { delete SESSIONS[hash]; return [] }
  return s.history || []
}
function pushHistory(hash, role, text) {
  const s = SESSIONS[hash] || { history: [] }
  s.history = (s.history || []).concat([{ role, text }]).slice(-CFG.max_history_turns)
  s.ts = nowMs()
  SESSIONS[hash] = s
  saveJSON(SESS_FILE, SESSIONS)
}

// --- extract plain text from a Baileys message --------------------------------
function extractText(m) {
  const msg = m.message || {}
  return msg.conversation
    || msg.extendedTextMessage?.text
    || msg.imageMessage?.caption
    || msg.videoMessage?.caption
    || ''
}

// --- main message handler -----------------------------------------------------
async function handleMessage(sock, m) {
  if (!m.message) return
  const jid = m.key.remoteJid || ''
  if (isJidGroup(jid) || isJidBroadcast(jid) || jid.endsWith('@newsletter') || jid === 'status@broadcast') return

  // Boss's OWN messages: if Boss texts an always-on chat himself, pause Jarvis there
  // so it doesn't talk over him. Otherwise ignore fromMe.
  if (m.key.fromMe) {
    if (ALWAYS_ON.has(jid)) { bossActive[jid] = nowMs(); console.log(`[jarvis] Boss active in ${sha(jid)} — paused there ${BOSS_ACTIVE_MS / 60000}min`) }
    return
  }

  const text = extractText(m)
  if (!text) return

  const hash = sha(jid)
  const alwaysOn = ALWAYS_ON.has(jid)
  // If Boss is personally chatting in an always-on chat right now, stay quiet.
  if (alwaysOn && bossActive[jid] && (nowMs() - bossActive[jid] < BOSS_ACTIVE_MS)) {
    console.log(`[jarvis] skipping ${hash} — Boss is active in this chat`); return
  }
  // SLIDING WINDOW: respond if named "jarvis", OR conversation already active
  // (within conversation_window_min), OR sender is an always-on contact (e.g. Anisha).
  const windowMs = (CFG.conversation_window_min || 30) * 60000
  const sess = SESSIONS[hash]
  const inWindow = sess && (nowMs() - (sess.ts || 0) < windowMs)
  if (!TRIGGER.test(text) && !inWindow && !alwaysOn) return   // <-- SILENT otherwise

  if (BLOCKLIST[hash]) { secLog({ event: 'blocked_sender_msg', sender: hash }); return }

  const lim = withinLimits(hash)
  if (!lim.ok) {
    secLog({ event: 'rate_limited', sender: hash, why: lim.why })
    if (!lim.silent && lim.why === 'sender-day') {
      await sock.sendMessage(jid, { text: CFG.throttle_message })
    }
    return
  }

  const name = m.pushName || 'unknown'
  console.log(`[jarvis] activated by ${hash} (${name}): ${text.slice(0, 60)}`)

  // typing indicator + human-like delay (anti-ban)
  try { await sock.sendPresenceUpdate('composing', jid) } catch {}
  await sleep(rand(CFG.reply_min_delay_ms, CFG.reply_max_delay_ms))

  const romantic = ROMANTIC.has(jid)
  let reply = ''
  if (romantic) {
    // Anisha etc. → "as Ujjawal" romantic persona (sandboxed worker, unsigned)
    const res = await callWorker(text.slice(0, CFG.rate.max_input_chars), getHistory(hash), name, 'romantic')
    if (res.error) { secLog({ event: 'worker_error', sender: hash, err: res.error }); console.error('[worker]', res.error) }
    reply = (res.reply || '').trim()
  } else {
    // everyone else → the REAL Jarvis (jarvis-core): performs tasks here, sends result.
    try {
      reply = await callRealJarvis(text.slice(0, CFG.rate.max_input_chars), name, hash)
    } catch (e) {
      console.error('[jarvis-core] unreachable, falling back to sandboxed worker:', e?.message)
      secLog({ event: 'core_fallback', sender: hash, err: String(e?.message) })
      const res = await callWorker(text.slice(0, CFG.rate.max_input_chars), getHistory(hash), name, 'twin')
      reply = (res.reply || '').trim()
    }
  }
  try { await sock.sendPresenceUpdate('paused', jid) } catch {}
  if (!reply) return

  const { redacted } = canary(reply, hash)
  reply = redacted

  recordHit(hash, lim.arr)
  pushHistory(hash, 'user', text)
  pushHistory(hash, 'assistant', reply)

  // romantic contacts → reply UNSIGNED (as Ujjawal); everyone else → 🤖 Jarvis signed
  await sock.sendMessage(jid, { text: romantic ? reply : (CFG.signature + reply) })
  replyCounter++
  if (replyCounter % CFG.after_n_replies_pause.count === 0) {
    console.log('[jarvis] cooldown pause'); await sleep(CFG.after_n_replies_pause.pause_ms)
  }
}

// --- outbound relay: Boss approves a task in Telegram → reply lands here -------
// The Telegram bridge appends {id, jid, text} lines to whatsapp_outbox.jsonl when
// Boss answers a pending task. We tail it from a persisted byte-offset and send
// each as Jarvis (with signature) to the original sender.
let activeSock = null
const OUTBOX_FILE = join(STATE_DIR, 'whatsapp_outbox.jsonl')
const OFFSET_FILE = join(STATE_DIR, '.outbox_offset')

function readOffset() { try { return parseInt(readFileSync(OFFSET_FILE, 'utf8'), 10) || 0 } catch { return 0 } }
function writeOffset(n) { try { writeFileSync(OFFSET_FILE, String(n)) } catch {} }

async function pollOutbox() {
  if (!activeSock) return
  let raw
  try { raw = readFileSync(OUTBOX_FILE, 'utf8') } catch { return }   // file may not exist yet
  const off = readOffset()
  if (raw.length <= off) { if (raw.length < off) writeOffset(raw.length); return }
  const fresh = raw.slice(off)
  writeOffset(raw.length)                                           // advance first (avoid resend on crash)
  for (const line of fresh.split('\n')) {
    const s = line.trim()
    if (!s) continue
    let obj
    try { obj = JSON.parse(s) } catch { continue }
    if (!obj.jid || !obj.text) continue
    try {
      await activeSock.sendPresenceUpdate('composing', obj.jid).catch(() => {})
      await sleep(rand(CFG.reply_min_delay_ms, CFG.reply_max_delay_ms))
      const { redacted } = canary(String(obj.text), sha(obj.jid))
      // signed:false → send in Boss's own voice (no Jarvis signature), e.g. a
      // flirty line to Anisha. Default (signed omitted/true) → 🤖 Jarvis signature.
      const outText = (obj.signed === false) ? redacted : (CFG.signature + redacted)
      await activeSock.sendMessage(obj.jid, { text: outText })
      pushHistory(sha(obj.jid), 'assistant', redacted)
      secLog({ event: 'task_reply_sent', id: obj.id || null, sender: sha(obj.jid) })
      console.log(`[jarvis] ✅ Boss-approved reply sent (id=${obj.id || '?'})`)
    } catch (e) { console.error('[outbox] send failed', e?.message) }
  }
}
setInterval(() => { pollOutbox().catch(() => {}) }, 3000)

// --- connection lifecycle -----------------------------------------------------
let reconnectDelay = 2000   // backoff so a 405 storm doesn't hammer WhatsApp

async function start() {
  const { state, saveCreds } = await useMultiFileAuthState(join(__dirname, 'auth_state'))
  const { version } = await fetchLatestBaileysVersion()   // current WA-web version → avoids 405
  console.log('[jarvis] using WA version', version.join('.'))
  const sock = makeWASocket({
    version,
    auth: { creds: state.creds, keys: makeCacheableSignalKeyStore(state.keys, logger) },
    logger,
    browser: Browsers.ubuntu('Chrome'),   // stable desktop fingerprint
    markOnlineOnConnect: false,           // don't flip Boss's phone to "online via linked device"
    syncFullHistory: false,
  })

  sock.ev.on('creds.update', saveCreds)

  sock.ev.on('connection.update', (u) => {
    const { connection, lastDisconnect, qr } = u
    if (qr) {
      console.log('\n📱 Scan this QR in WhatsApp → Settings → Linked Devices → Link a Device:\n')
      qrcode.generate(qr, { small: true })
      try { writeFileSync(join(STATE_DIR, 'qr.txt'), qr) } catch {}  // raw string → render as PNG
    }
    if (connection === 'open') {
      reconnectDelay = 2000; activeSock = sock
      console.log('✅ Jarvis WhatsApp gateway connected. Watching DMs (silent unless named "jarvis").')
      // verify always-on numbers actually exist on WhatsApp + log canonical jid
      ;(async () => {
        for (const j of ALWAYS_ON) {
          const num = j.split('@')[0]
          try {
            const res = await sock.onWhatsApp(num)
            console.log(`[verify] ${num} →`, JSON.stringify(res))
          } catch (e) { console.log(`[verify] ${num} error: ${e?.message}`) }
        }
      })()
    }
    if (connection === 'close') {
      activeSock = null
      const code = new Boom(lastDisconnect?.error)?.output?.statusCode
      const loggedOut = code === DisconnectReason.loggedOut
      console.log(`⚠️  Connection closed (code ${code}).`, loggedOut ? 'Logged out — delete whatsapp/auth_state and re-scan QR.' : `Reconnecting in ${reconnectDelay / 1000}s…`)
      if (!loggedOut) {
        setTimeout(start, reconnectDelay)
        reconnectDelay = Math.min(reconnectDelay * 2, 30000)   // exponential backoff, cap 30s
      }
    }
  })

  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify') return
    for (const m of messages) {
      try { await handleMessage(sock, m) } catch (e) { console.error('[handler]', e) }
    }
  })

  // --- contact capture (for owner-directed lookups, e.g. find "Anisha") -------
  // Accumulate jid -> name into state/contacts.json as WhatsApp syncs them.
  const CONTACTS_FILE = join(STATE_DIR, 'contacts.json')
  const loadContacts = () => { try { return JSON.parse(readFileSync(CONTACTS_FILE, 'utf8')) } catch { return {} } }
  const mergeContacts = (list) => {
    if (!Array.isArray(list) || !list.length) return
    const map = loadContacts()
    let added = 0
    for (const c of list) {
      const jid = c?.id || c?.jid
      if (!jid || !jid.endsWith('@s.whatsapp.net')) continue
      const name = c?.name || c?.notify || c?.verifiedName || ''
      if (name && map[jid] !== name) { map[jid] = name; added++ }
      else if (!map[jid]) { map[jid] = name || '' }
    }
    if (added) { try { writeFileSync(CONTACTS_FILE, JSON.stringify(map)) } catch {} ; console.log(`[contacts] +${added} (total ${Object.keys(map).length})`) }
  }
  sock.ev.on('contacts.upsert', mergeContacts)
  sock.ev.on('contacts.set', ({ contacts }) => mergeContacts(contacts))
  sock.ev.on('contacts.update', mergeContacts)
  sock.ev.on('messaging-history.set', ({ contacts }) => mergeContacts(contacts))
}

start().catch(e => { console.error('FATAL', e); process.exit(1) })
