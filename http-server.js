const express = require("express");
const { createServer } = require("http");
const authBearerParser = require("auth-bearer-parser").default;
const path = require("path");

const app = express();
const httpServer = createServer(app);

app.use(express.json());
app.use(authBearerParser());

app.use(
    "/",
    express.static(
        path.join(__dirname, "frontend", "home")
    )
);

app.use(
    "/admin",
    express.static(
        path.join(__dirname, "frontend", "admin")
    )
);
app.use(
    "/stats",
    express.static(
        path.join(__dirname, "frontend", "stats")
    )
);

app.get("/", (req, res) => {
    res.sendFile(
        path.join(__dirname, "frontend", "home", "index.html")
    );
});

app.get("/admin", (req, res) => {
    res.sendFile(
        path.join(__dirname, "frontend", "admin", "index.html")
    );
});

app.get("/stats", (req, res) => {
    res.sendFile(
        path.join(__dirname, "frontend", "stats", "index.html")
    );
});

module.exports = { app, httpServer};