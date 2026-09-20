const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const config = require('../config');
const store = require('../store');

const router = express.Router();

// POST /api/auth/register  { username, password }
router.post('/register', async (req, res) => {
  const { username, password } = req.body || {};

  if (!username || !password) {
    return res.status(400).json({ error: 'Потрібні username і password' });
  }
  if (username.length < 3) {
    return res.status(400).json({ error: 'username має містити щонайменше 3 символи' });
  }
  if (password.length < 6) {
    return res.status(400).json({ error: 'password має містити щонайменше 6 символів' });
  }
  if (store.findByUsername(username)) {
    return res.status(409).json({ error: 'Користувач з таким username вже існує' });
  }

  const passwordHash = await bcrypt.hash(password, 10);

  const user = store.add({
    username,
    passwordHash,
    role: 'user',
    createdAt: new Date().toISOString(),
  });

  res.status(201).json({ id: user.id, username: user.username, role: user.role });
});

// POST /api/auth/login  { username, password }
router.post('/login', async (req, res) => {
  const { username, password } = req.body || {};
  const user = username && store.findByUsername(username);

  const ok = user && (await bcrypt.compare(password || '', user.passwordHash));
  if (!ok) {
    return res.status(401).json({ error: 'Невірний username або пароль' });
  }

  const payload = {
    sub: user.id,
    username: user.username,
    role: user.role,
    fullName: config.student.fullName,
    group: config.student.group,
    variant: config.student.variant,
  };

  const authToken = jwt.sign(payload, config.jwtSecret, {
    expiresIn: config.tokenTtl,
  });

  res.json({ authToken, expiresIn: config.tokenTtl });
});

module.exports = router;
