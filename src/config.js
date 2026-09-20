require('dotenv').config();

const variant = Number(process.env.VARIANT);
if (!Number.isInteger(variant)) {
  throw new Error('VARIANT у .env має бути цілим числом');
}

module.exports = {
  port: process.env.PORT || 3000,
  jwtSecret: process.env.JWT_SECRET,
  student: {
    fullName: `${process.env.STUDENT_SURNAME} ${process.env.STUDENT_INITIALS}`,
    group: process.env.STUDENT_GROUP,
    variant,
  },
  tokenTtl: 60 + variant,
  admin: {
    username: process.env.ADMIN_USERNAME,
    password: process.env.ADMIN_PASSWORD,
  },
};
