const mongoose = require("mongoose");

const fragilitySchema = new mongoose.Schema({
    imName: {
        type: String,
        required: [true, "Fragility function must have intensity measure name"]
    },

    unitOfMeasure: {
        type: String,
        required: [true, "Fragility function must have unit of measure of intensity measure"]
    },

    component: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Component',
        required: [true, "Fragility function must be tied to Component"],
        unique: true
    },
},
{timestamps: true});

module.exports = mongoose.model("Fragility", fragilitySchema);
