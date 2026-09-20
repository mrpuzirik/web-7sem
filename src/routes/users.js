const express = require('express');
const store = require('../store');
const { authenticate, authorize } = require('../middleware/auth');

const router = express.Router();

const publicView = ({ passwordHash, ...rest }) => rest;

// GET /api/profile
router.get('/profile', authenticate, (req, res) => {
  res.json({ message: 'Токен валідний', tokenPayload: req.user });
});

// GET /api/user/dashboard
router.get('/user/dashboard', authenticate, authorize('user', 'admin'), (req, res) => {
  res.json({ message: `Вітаю, ${req.user.username}! Це панель користувача.` });
});

// GET /api/users
router.get('/users', authenticate, authorize('admin'), (req, res) => {
  res.json(store.all().map(publicView));
});

// PATCH /api/users/:id/role
router.patch('/users/:id/role', authenticate, authorize('admin'), (req, res) => {
  const { role } = req.body || {};
  if (!['user', 'admin'].includes(role)) {
    return res.status(400).json({ error: 'role має бути "user" або "admin"' });
  }
  const user = store.update(Number(req.params.id), { role });
  if (!user) return res.status(404).json({ error: 'Користувача не знайдено' });
  res.json(publicView(user));
});

// DELETE /api/users/:id
router.delete('/users/:id', authenticate, authorize('admin'), (req, res) => {
  const id = Number(req.params.id);
  if (id === req.user.sub) {
    return res.status(400).json({ error: 'Не можна видалити самого себе' });
  }
  if (!store.remove(id)) {
    return res.status(404).json({ error: 'Користувача не знайдено' });
  }
  res.status(204).end();
});

module.exports = router;
