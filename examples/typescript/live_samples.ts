// Run with: npx ts-node live_samples.ts
// Dependencies: npm install ws axios

import axios from "axios";
import WebSocket from "ws";

const BASE_URL = process.env.XINGSHU_BCI_BASE_URL || "http://127.0.0.1:0";
const TOKEN = process.env.XINGSHU_BCI_TOKEN;

if (!TOKEN) {
  console.error("Set XINGSHU_BCI_TOKEN before running.");
  process.exit(1);
}

async function main() {
  const http = axios.create({
    baseURL: BASE_URL,
    headers: { Authorization: `Bearer ${TOKEN}` },
    timeout: 10000
  });

  const version = await http.get("/v1/version");
  console.log("version:", version.data);

  const status = await http.get("/v1/status");
  console.log("status:", status.data.state);

  const wsUrl = `${BASE_URL.replace(/^http/, "ws")}/v1/events?token=${TOKEN}&events=samples,analysis`;
  console.log("connecting", wsUrl);
  const ws = new WebSocket(wsUrl);

  ws.on("open", () => console.log("ws open"));
  ws.on("message", (raw) => {
    const envelope = JSON.parse(raw.toString());
    if (envelope.type === "samples") {
      const data = envelope.payload?.data;
      console.log("samples ch0[0] =", data?.[0]?.[0]);
    } else if (envelope.type === "analysis") {
      console.log("analysis focus =", envelope.payload?.focus);
    }
  });
  ws.on("close", () => console.log("ws closed"));
  ws.on("error", (err) => console.error("ws error", err));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
