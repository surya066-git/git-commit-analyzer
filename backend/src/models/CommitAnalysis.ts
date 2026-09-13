import mongoose, { Schema, Document } from 'mongoose';

export interface ICommitAnalysis extends Document {
    repositoryId?: mongoose.Types.ObjectId;
    userId?: mongoose.Types.ObjectId;
    hash?: string; // Optional for manual ad-hoc analysis
    message: string;
    category: string;
    confidence: number;
    qualityScore: number;
    qualityLevel: string;
    qualityBreakdown: {
        clarity: number;
        specificity: number;
        actionability: number;
        context: number;
        consistency: number;
    };
    issues: string[];
    suggestion: string;
    consistency: {
        status: string;
        reason: string;
    };
    createdAt: Date;
}

const CommitAnalysisSchema: Schema = new Schema({
    repositoryId: { type: Schema.Types.ObjectId, ref: 'Repository' },
    userId: { type: Schema.Types.ObjectId, ref: 'User' },
    hash: { type: String },
    message: { type: String, required: true },
    category: { type: String, required: true },
    confidence: { type: Number, required: true },
    qualityScore: { type: Number, required: true },
    qualityLevel: { type: String, required: true },
    qualityBreakdown: {
        clarity: { type: Number, required: true },
        specificity: { type: Number, required: true },
        actionability: { type: Number, required: true },
        context: { type: Number, required: true },
        consistency: { type: Number, required: true }
    },
    issues: [{ type: String }],
    suggestion: { type: String, required: true },
    consistency: {
        status: { type: String, required: true },
        reason: { type: String, required: true }
    }
}, {
    timestamps: true
});

// Index for efficient querying by repository
CommitAnalysisSchema.index({ repositoryId: 1 });
CommitAnalysisSchema.index({ userId: 1 });

export default mongoose.models.CommitAnalysis || mongoose.model<ICommitAnalysis>('CommitAnalysis', CommitAnalysisSchema);
