const express = require("express");

const componentController = require("../controllers/componentController");

const router = express.Router();

router.route("/")
    .get(componentController.getAllComponents)
    .post(componentController.createComponent)

router.route("/:name")
    .get(componentController.getOneComponent)
    .patch(componentController.updateComponent)
    .delete(componentController.deleteComponent)

module.exports = router;
