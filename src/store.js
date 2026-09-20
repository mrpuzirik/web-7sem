const fs = require('fs');
const path = require('path');

const DIR = path.join(__dirname, '..', 'data');
const FILE = path.join(DIR, 'users.json');

function load() {
  if (!fs.existsSync(FILE)) return [];
  return JSON.parse(fs.readFileSync(FILE, 'utf8'));
}

function save(users) {
  fs.mkdirSync(DIR, { recursive: true });
  fs.writeFileSync(FILE, JSON.stringify(users, null, 2));
}

module.exports = {
  all: () => load(),
  findByUsername: (username) =>
    load().find((u) => u.username.toLowerCase() === username.toLowerCase()),
  findById: (id) => load().find((u) => u.id === id),
  add(user) {
    const users = load();
    user.id = users.length ? Math.max(...users.map((u) => u.id)) + 1 : 1;
    users.push(user);
    save(users);
    return user;
  },
  update(id, patch) {
    const users = load();
    const user = users.find((u) => u.id === id);
    if (!user) return null;
    Object.assign(user, patch);
    save(users);
    return user;
  },
  remove(id) {
    const users = load();
    const idx = users.findIndex((u) => u.id === id);
    if (idx === -1) return false;
    users.splice(idx, 1);
    save(users);
    return true;
  },
};
