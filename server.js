require("dotenv").config();

const path = require("path");
const http = require("http");
const crypto = require("crypto");
const express = require("express");
const { Server } = require("socket.io");

const STUDENT_NAME = process.env.STUDENT_NAME || "Прізвище Ім'я По батькові";
const GROUP = process.env.STUDENT_GROUP || "ХХ-ХХ";
const VARIANT_N = parseInt(process.env.VARIANT_N || "5", 10);

const AUTO_INTERVAL = 10 + VARIANT_N;
const AUTO_TEXT =
  `Автоматичне повідомлення від ст. ${STUDENT_NAME} ` +
  `гр. ${GROUP} Варіант ${VARIANT_N}`;

const ROOM = "chat";
const HISTORY_SIZE = 50;
const MAX_TEXT_LEN = 1000;
const MAX_NICK_LEN = 24;
const PORT = parseInt(process.env.PORT || "5000", 10);

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static(path.join(__dirname, "public")));

const users = new Map();
const history = [];
let nextAutoAt = Date.now() + AUTO_INTERVAL * 1000;

const pad = (n) => String(n).padStart(2, "0");
function timeNow() {
  const d = new Date();
  return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

function makeMessage(text, author, kind = "user") {
  return {
    id: crypto.randomUUID(),
    kind,
    author,
    text,
    time: timeNow(),
  };
}

function publish(message) {
  history.push(message);
  if (history.length > HISTORY_SIZE) history.shift();
  io.to(ROOM).emit("message", message);
}

function broadcastUsers() {
  const list = [...users.values()].sort((a, b) =>
    a.toLowerCase().localeCompare(b.toLowerCase())
  );
  io.to(ROOM).emit("users", list);
}

const secondsToNextAuto = () => Math.max(0, (nextAutoAt - Date.now()) / 1000);

setInterval(() => {
  nextAutoAt = Date.now() + AUTO_INTERVAL * 1000;
  publish(makeMessage(AUTO_TEXT, "Авто", "auto"));
  io.to(ROOM).emit("auto_tick", { next_in: AUTO_INTERVAL });
}, AUTO_INTERVAL * 1000);

io.on("connection", (socket) => {
  socket.on("join", (data) => {
    const nick = String((data && data.nick) || "").trim().slice(0, MAX_NICK_LEN);

    if (!nick) {
      socket.emit("join_error", "Введіть нікнейм.");
      return;
    }
    const taken = [...users.entries()].some(
      ([sid, u]) => sid !== socket.id && u.toLowerCase() === nick.toLowerCase()
    );
    if (taken) {
      socket.emit("join_error", `Нікнейм «${nick}» уже зайнятий. Оберіть інший.`);
      return;
    }
    if (users.has(socket.id)) return;

    users.set(socket.id, nick);
    socket.join(ROOM);
    socket.emit("joined", {
      nick,
      history: [...history],
      interval: AUTO_INTERVAL,
      next_in: secondsToNextAuto(),
    });
    publish(makeMessage(`${nick} приєднався до чату`, "Чат", "system"));
    broadcastUsers();
  });

  socket.on("message", (data) => {
    const nick = users.get(socket.id);
    if (!nick) return; // не авторизований учасник
    const text = String((data && data.text) || "").trim().slice(0, MAX_TEXT_LEN);
    if (text) publish(makeMessage(text, nick));
  });

  socket.on("typing", (isTyping) => {
    const nick = users.get(socket.id);
    if (nick) socket.to(ROOM).emit("typing", { nick, typing: Boolean(isTyping) });
  });

  socket.on("disconnect", () => {
    const nick = users.get(socket.id);
    if (!nick) return;
    users.delete(socket.id);
    publish(makeMessage(`${nick} залишив чат`, "Чат", "system"));
    io.to(ROOM).emit("typing", { nick, typing: false });
    broadcastUsers();
  });
});

server.listen(PORT, () => {
  console.log(`Чат: http://localhost:${PORT}`);
  console.log(`Автоповідомлення кожні ${AUTO_INTERVAL} с: ${AUTO_TEXT}`);
});
