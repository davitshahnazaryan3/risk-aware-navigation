const Component = require("../models/componentModel");

exports.getAllComponents = async (req, res, next) => {

    try {
        const components = await Component.find()
            .populate({path: 'fragilityFunctions', select: 'imName unitOfMeasure'})
            .populate({path: 'damageStates', select: 'name mean dispersion'});

        res.status(200).json({
            status: "success",
            results: components.length,
            data: {
                components
            }
        })
    } catch (e) {
        res.status(400).json({
            status: "failed to fetch components",
        });
    }
};

exports.getOneComponent = async (req, res, next) => {
    try {
        const component = await Component.findOne({ "name": req.params.name })
            .populate({path: 'fragilityFunctions', select: 'imName unitOfMeasure'})
            .populate({path: 'damageStates', select: 'name mean dispersion'})
            .populate({path: 'coordinates', select: 'topLeft topRight bottomLeft bottomRight influenceRadius'});

        if (!component) {
            return res.status(404).json({
                status: "fail",
                message: "component not found"
            })
        }

        res.status(200).json({
            status: "success",

            data: {
                component,
            },
        });
    } catch (e) {
        res.status(400).json({
            status: "failed to fetch component",
        });
    }
};

exports.createComponent = async (req, res, next) => {
    try {
        const component = await Component.create(req.body);

        res.status(201).json({
            status: "component successfully created",

            data: {
                component,
            },
        });
    } catch (e) {
        res.status(400).json({
            status: "failed to create component. Component with name already exists",
        });
    }
};

exports.updateComponent = async (req, res, next) => {
    try {
        const component = await Component.findOneAndUpdate({ "name": req.params.name },
        req.body, {
            new: true,
            runValidators: true,
        });

        res.status(201).json({
            status: "success",

            data: {
                component,
            },
        });
    } catch (e) {
        res.status(404).json({
            status: "failed to update component",
        });
    }
};

exports.deleteComponent = async (req, res, next) => {
    try {
        const component = await Component.findOneAndDelete({ "name": req.params.name });

        if (!component) {
            return res.status(404).json({
                status: "fail",
                message: "component not found"
            })
        }

        res.status(204).json({
            status: "success",
        });

    } catch (e) {
        res.status(404).json({
            status: "failed to delete component",
        });
    }
};
