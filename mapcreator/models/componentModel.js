const mongoose = require("mongoose");

const componentSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, "Component must have name"],
        unique: true
    },

    description: {
        type: String,
    },

    reference: {
        type: String,
    },

    cells: {
        type: [Number],
    },

    influence_cells: {
        type: [Number],
    },

},
{timestamps: true},
{id: false});

componentSchema.virtual('fragilityFunctions', {
    ref: 'Fragility',
    localField: '_id',
    foreignField: 'component',
});

componentSchema.virtual('damageStates', {
    ref: 'Damage',
    localField: '_id',
    foreignField: 'component',
});

componentSchema.virtual('coordinates', {
    ref: 'Coordinates',
    localField: '_id',
    foreignField: 'component',
});

componentSchema.virtual('realCoordinates', {
    ref: 'RealCoordinates',
    localField: '_id',
    foreignField: 'component',
});

componentSchema.set('toObject', { virtuals: true });
componentSchema.set('toJSON', { virtuals: true });

module.exports = mongoose.model("Component", componentSchema);
