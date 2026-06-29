import express from 'express';
import { WhatsAppClient } from './whatsapp';
import path from 'path';
import fs from 'fs';

const PORT = parseInt(process.env.PORT || '4000', 10);
const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, '..', 'data');
const BACKEND_WEBHOOK = process.env.BACKEND_WEBHOOK_URL || 'http://backend:8000/api/v1/webhooks/whatsapp-inbound';

if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

const app = express();
app.use(express.json());

let client: WhatsAppClient;

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', connected: client?.isConnected ?? false });
});

app.get('/qr', async (_req, res, next) => {
  try {
    const qr = client?.lastQR;
    if (!qr) {
      return res.status(404).json({ error: 'No QR available. Check if already connected.' });
    }
    res.json({ qr });
  } catch (err) {
    next(err);
  }
});

app.get('/qr/image', async (_req, res, next) => {
  try {
    const qr = client?.lastQR;
    if (!qr) {
      return res.status(404).json({ error: 'No QR available' });
    }
    const { toDataURL } = await import('qrcode');
    const dataUrl = await toDataURL(qr, { width: 400, margin: 2 });
    const base64 = dataUrl.replace(/^data:image\/png;base64,/, '');
    const img = Buffer.from(base64, 'base64');
    res.writeHead(200, {
      'Content-Type': 'image/png',
      'Content-Length': img.length,
    });
    res.end(img);
  } catch (err) {
    next(err);
  }
});

app.get('/status', (_req, res, next) => {
  try {
    res.json({
      connected: client?.isConnected ?? false,
      phone: client?.phoneNumber || null,
    });
  } catch (err) {
    next(err);
  }
});

app.post('/send', async (req, res) => {
  try {
    const { to, message } = req.body;
    if (!to || !message) {
      return res.status(400).json({ error: 'Missing required fields: to, message' });
    }
    const jid = to.includes('@s.whatsapp.net') ? to : `${to}@s.whatsapp.net`;
    const sent = await client?.sendMessage(jid, message);
    if (sent) {
      res.json({ success: true, id: sent.key?.id });
    } else {
      res.status(502).json({ error: 'Failed to send message' });
    }
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/disconnect', async (_req, res, next) => {
  try {
    await client?.disconnect();
    res.json({ success: true });
  } catch (err) {
    next(err);
  }
});

app.use((err: any, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: err?.message || 'Internal server error' });
});

async function start() {
  client = new WhatsAppClient(DATA_DIR, BACKEND_WEBHOOK);
  await client.initialize();
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`WhatsApp Bridge running on port ${PORT}`);
    console.log(`Data directory: ${DATA_DIR}`);
    console.log(`Webhook URL: ${BACKEND_WEBHOOK}`);
  });
}

start().catch(console.error);
