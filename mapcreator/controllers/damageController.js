const Damage = require("../models/damageModel");
const Component = require("../models/componentModel");


exports.assignDamageState = async (req, res, next) => {

    try {

        // Find Component
        const component = await Component.findById({ "_id": req.body.component });

        if (!component) {
            return res.status(404).json({
                status: "fail",
                message: "component not found"
            })
        }

        // Create damage state
        const damage = await Damage.create(req.body);

        res.status(201).json({
            status: "success",

            data: {
              damage,
            },
        });

    } catch (e) {
        res.status(400).json({
            status: "failed to add damage state",
        });
    }
};

exports.updateDamageState = async (req, res, next) => {

    try {

        const damage = await Damage.findOneAndUpdate({ "component": req.body.component, "name": req.body.name },
            req.body, {
                new: true,
                runValidators: true,
        });

        res.status(201).json({
            status: "success",

            data: {
              damage,
            },
        });
    } catch (e) {
        res.status(404).json({
            status: "failed to update damage state",
        });
    }
};

exports.deleteDamageState = async (req, res, next) => {

    try {
        const damage = await Damage.findOneAndDelete({ "component": req.body.component, "name": req.body.name });

        if (!damage) {
            return res.status(404).json({
                status: "fail",
                message: "Damage state or component not found"
            })
        }

        res.status(204).json({
            status: "success",
        });

    } catch (e) {
        res.status(400).json({
            status: "failed to delete damage state",
        });
    }
};
