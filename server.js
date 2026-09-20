const express = require('express');
const bcrypt = require('bcryptjs');
const config = require('./src/config');
const store = require('./src/store');

const app = express();
app.use(express.json());

app.use('/api/auth', require('./src/routes/auth'));
app.use('/api', require('./src/routes/users'));

app.use((req, res) => res.status(404).json({ error: 'Маршрут не знайдено' }));

async function seedAdmin() {
  const { username, password } = config.admin;
  if (!username || !password || store.findByUsername(username)) return;
  store.add({
    username,
    passwordHash: await bcrypt.hash(password, 10),
    role: 'admin',
    createdAt: new Date().toISOString(),
  });
  console.log(`Створено адміністратора "${username}"`);
}

seedAdmin().then(() =>
  app.listen(config.port, () =>
    console.log(`Сервер: http://localhost:${config.port} | TTL токена: ${config.tokenTtl} с`)
  )
);
