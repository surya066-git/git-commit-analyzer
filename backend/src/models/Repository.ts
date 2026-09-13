import mongoose, { Schema, Document } from 'mongoose';

export interface IRepository extends Document {
    githubId: string;
    userId: mongoose.Types.ObjectId;
    name: string;
    fullName: string;
    description?: string;
    url: string;
    isPrivate: boolean;
    defaultBranch: string;
    language?: string;
    stars: number;
    lastSyncedAt?: Date;
    createdAt: Date;
    updatedAt: Date;
}

const RepositorySchema: Schema = new Schema({
    githubId: { type: String, required: true, unique: true },
    userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    name: { type: String, required: true },
    fullName: { type: String, required: true },
    description: { type: String },
    url: { type: String, required: true },
    isPrivate: { type: Boolean, default: false },
    defaultBranch: { type: String, default: 'main' },
    language: { type: String },
    stars: { type: Number, default: 0 },
    lastSyncedAt: { type: Date }
}, {
    timestamps: true
});

// Index for efficient querying by user
RepositorySchema.index({ userId: 1 });

export default mongoose.models.Repository || mongoose.model<IRepository>('Repository', RepositorySchema);
