const jwt = require('jsonwebtoken');
const config = require('../config');

function authenticate(req, res, next) {
  const header = req.headers.authorization || '';
  const [scheme, token] = header.split(' ');

  if (scheme !== 'Bearer' || !token) {
    return res
      .status(401)
      .json({ error: 'Потрібен заголовок Authorization: Bearer <token>' });
  }

  try {
    req.user = jwt.verify(token, config.jwtSecret);
    next();
  } catch (err) {
    const message =
      err.name === 'TokenExpiredError'
        ? 'Термін дії токена минув'
        : 'Недійсний токен';
    return res.status(401).json({ error: message });
  }
}

const authorize =
  (...roles) =>
  (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res
        .status(403)
        .json({ error: `Доступ заборонено. Потрібна роль: ${roles.join(' / ')}` });
    }
    next();
  };

module.exports = { authenticate, authorize };
