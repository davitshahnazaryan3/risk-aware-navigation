require('dotenv').config(); 


module.exports = {
    MONGO_IP: process.env.MONGO_IP || "mongo",
    MONGO_PORT: process.env.MONGO_PORT || 27017,
    MONGO_USER: process.env.MONGO_USER,
    MONGO_PASSWORD: process.env.MONGO_PASSWORD,
    DATABASE_NAME: process.env.DATABASE_NAME,
    PORT: process.env.PORT || 3000,
    DB_TYPE: process.env.DB_TYPE || "local",
};