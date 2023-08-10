const express = require("express");
const mongoose = require("mongoose");
const swaggerUi = require("swagger-ui-express");
const YAML = require("yamljs");
const swaggerDocument = YAML.load("./api/swagger/swagger.yaml");

const {
    MONGO_USER,
    MONGO_PASSWORD,
    DATABASE_NAME,
    DB_TYPE,
    PORT,
} = require("./config/config");

const componentRouter = require("./routes/componentRoutes");
const fragilityRouter = require("./routes/fragilityRoutes");
const damageRouter = require("./routes/damageRoutes");
const coordinatesRouter = require("./routes/coordinatesRoutes");
const realCoordinatesRouter = require("./routes/realCoordinatesRoutes");

const app = express();

let mongoURL;

// Mongo DB
if (DB_TYPE.toLowerCase() === "local") {
    mongoURL = `mongodb://localhost/${DATABASE_NAME}`;
} else {
    mongoURL = `mongodb+srv://${MONGO_USER}:${MONGO_PASSWORD}@cluster0.fnot2.mongodb.net/${DATABASE_NAME}?retryWrites=true`;
}

const connectWithRetry = () => {
    mongoose
    .connect(mongoURL, {})
    .then(() => console.log("successfully connected to db"))
    .catch((e) => {
        console.log(e);
        setTimeout(connectWithRetry, 5000);
    });
};

connectWithRetry();

// Run express app
app.use(express.json());

// Routes
app.get("/api/v1", (req, res) => {
    res.send("<h2>Inventory database app running</h2>")
});

app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocument));

app.use("/api/v1/component", componentRouter);
app.use("/api/v1/fragility", fragilityRouter);
app.use("/api/v1/damage", damageRouter);
app.use("/api/v1/coord", coordinatesRouter);
app.use("/api/v1/real", realCoordinatesRouter);

const port = PORT || 3000;

app.listen(port, () => console.log(`listening on port ${port}`));
