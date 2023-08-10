const express = require("express");

const coordinatesController = require("../controllers/coordinatesController");

const router = express.Router();


router.route("/")
    .post(coordinatesController.assignCoordinates)
    .patch(coordinatesController.updateCoordinates)
    .delete(coordinatesController.deleteCoordinates)

module.exports = router;
