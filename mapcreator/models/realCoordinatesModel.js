const mongoose = require("mongoose");


const realCoordinatesSchema = new mongoose.Schema({

    topLeft: {
        type: [Number],
        required: [true, "Top left coordinate must be defined"]
    },

    topRight: {
        type: [Number]
    },

    bottomLeft: {
        type: [Number]
    },

    bottomRight: {
        type: [Number],
        required: [true, "Bottom right coordinate must be defined"]
    },

    influenceRadius: {
        type: Number,
        default: 0.0
    },

    component: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Component',
        required: [true, "Coordinates must be tied to Component"]
    },

},
{timestamps: true});

module.exports = mongoose.model("RealCoordinates", realCoordinatesSchema);
