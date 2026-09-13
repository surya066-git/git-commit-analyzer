import React, { useEffect } from 'react';
import { useToast } from '../../context/ToastContext';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import './Toast.css';

export function ToastContainer() {
  const { toasts, removeToast } = useToast();

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onRemove={() => removeToast(toast.id)} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onRemove }: { toast: any, onRemove: () => void }) {
  useEffect(() => {
    if (toast.duration !== 0) {
      const timer = setTimeout(() => {
        onRemove();
      }, toast.duration || 3000);
      return () => clearTimeout(timer);
    }
  }, [toast, onRemove]);

  const Icon = {
    success: CheckCircle,
    error: AlertCircle,
    info: Info,
    warning: AlertTriangle,
  }[toast.type] || Info;

  return (
    <div className={`toast toast-${toast.type}`}>
      <div className="toast-icon">
        <Icon size={20} />
      </div>
      <div className="toast-content">
        {toast.title && <div className="toast-title">{toast.title}</div>}
        <div className="toast-message">{toast.message}</div>
      </div>
      <button className="toast-close" onClick={onRemove} aria-label="Close">
        <X size={16} />
      </button>
    </div>
  );
}
