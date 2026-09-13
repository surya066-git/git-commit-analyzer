import mongoose, { Schema, Document } from 'mongoose';

export interface IUser extends Document {
    githubId: string;
    username: string;
    displayName?: string;
    email?: string;
    avatarUrl?: string;
    accessToken: string;
    createdAt: Date;
    updatedAt: Date;
}

const UserSchema: Schema = new Schema({
    githubId: { type: String, required: true, unique: true },
    username: { type: String, required: true },
    displayName: { type: String },
    email: { type: String },
    avatarUrl: { type: String },
    accessToken: { type: String, required: true }
}, {
    timestamps: true
});

export default mongoose.models.User || mongoose.model<IUser>('User', UserSchema);
