import { Document, Schema } from 'mongoose';

// Interfaz para el documento de auditoría
export interface IAuditDocument extends Document {
  user: string;
  path: string;
  managedRead: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// Esquema de MongoDB para auditoría
export const AuditSchema = new Schema<IAuditDocument>({
  user: {
    type: String,
    required: true,
    index: true
  },
  path: {
    type: String,
    required: true,
    index: true
  },
  managedRead: {
    type: Boolean,
    required: true,
    default: false
  }
}, {
  timestamps: true,
  collection: 'audit_logs'
});
