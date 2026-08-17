import QRCode from 'qrcode'
import { readFileSync } from 'node:fs'
const s = readFileSync('state/qr.txt', 'utf8').trim()
await QRCode.toFile('state/qr.png', s, { width: 600, margin: 2, errorCorrectionLevel: 'M' })
console.log('PNG written: whatsapp/state/qr.png')
