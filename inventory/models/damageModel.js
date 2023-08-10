const mongoose = require("mongoose");


const damageSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, "Damage State must have name"]
    },

    alternative_name: {
        type: String,
    },

    mean: {
        type: Number,
        required: [true, "Damage State must have mean"]
    },

    dispersion: {
        type: Number,
        required: [true, "Damage State must have dispersion"]
    },

    description: {
        type: String,
    },

    consequence: {
        type: String,
    },

    component: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Component',
        required: [true, "Damage state must be tied to Component"]
    },

},
{timestamps: true});

damageSchema.index({ name: 1, component: 1 }, { unique: true });

module.exports = mongoose.model("Damage", damageSchema);
