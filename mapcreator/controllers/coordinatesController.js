const Coordinates = require("../models/coordinatesModel");
const Component = require("../models/componentModel");


exports.assignCoordinates = async (req, res, next) => {

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
        const coordinates = await Coordinates.create(req.body);

        res.status(201).json({
            status: "coordinates successfully added to component",

            data: {
              coordinates,
            },
        });

    } catch (e) {
        res.status(400).json({
            status: "failed to add coordinates",
        });
    }
};

exports.updateCoordinates = async (req, res, next) => {

    try {

        const coordinates = await Coordinates.findByIdAndUpdate({ "_id": req.body._id },
            req.body, {
                new: true,
                runValidators: true,
        });

        res.status(201).json({
            status: "successfully updated coordinates",

            data: {
              coordinates,
            },
        });
    } catch (e) {
        res.status(404).json({
            status: "failed to update coordinates",
        });
    }
};

exports.deleteCoordinates = async (req, res, next) => {

    try {
        const coordinates = await Coordinates.findByIdAndDelete({ "_id": req.body._id });

        if (!coordinates) {
            return res.status(404).json({
                status: "fail",
                message: "Coordinates not found"
            })
        }

        res.status(204).json({
            status: "successfully deleted coordinates",
        });

    } catch (e) {
        res.status(400).json({
            status: "failed to delete coordinates",
        });
    }
};
