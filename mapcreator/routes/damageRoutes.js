const express = require("express");

const damageController = require("../controllers/damageController");

const router = express.Router();


router.route("/")
    .post(damageController.assignDamageState)
    .patch(damageController.updateDamageState)
    .delete(damageController.deleteDamageState)

module.exports = router;
