const Fragility = require("../models/fragilityModel");
const Component = require("../models/componentModel");


exports.getAllFragility = async (req, res, next) => {

    try {
        const fragility = await Fragility.find();

        res.status(200).json({
            status: "success",
            results: fragility.length,
            data: {
                fragility
            }
        })

    } catch (e) {
        res.status(400).json({
            status: "failed to fetch fragility functions",
        });
    }
};


exports.assignFragility = async (req, res, next) => {

    try {
        // verify component exists
        const component = await Component.findById({ "_id": req.body.component })

        if (!component) {
            return res.status(404).json({
                status: "fail",
                message: "component not found"
            })
        };

        const fragility = await Fragility.create(req.body);

        res.status(201).json({
            status: "success",

            data: {
              fragility,
            },
        });

    } catch (e) {
        res.status(400).json({
            status: "failed to add fragility function",
        });
    }
};

exports.updateFragility = async (req, res, next) => {

    try {
        // verify component exists
        const component = await Component.findById({ "_id": req.body.component })

        if (!component) {
            return res.status(404).json({
                status: "fail",
                message: "component not found"
            })
        };

        const fragility = await Fragility.findOneAndUpdate({"component": req.body.component },
            req.body, {
                new: true,
                runValidators: true,
        });

        res.status(201).json({
            status: "success",

            data: {
              fragility,
            },
        });

    } catch (e) {
        res.status(404).json({
            status: "fail",
        });
    }
};

