const express = require("express");

const fragilityController = require("../controllers/fragilityController");

const router = express.Router();


router.route("/")
    .get(fragilityController.getAllFragility)
    .post(fragilityController.assignFragility)
    .patch(fragilityController.updateFragility)

module.exports = router;
