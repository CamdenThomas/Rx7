// Short messages that say what just happened to what he did, then leave on their own.

export interface Toast {
  id: number;
  text: string;
  tone: 'ok' | 'info' | 'warn';
}

let next = 1;

class Toasts {
  list = $state<Toast[]>([]);

  push(text: string, tone: Toast['tone'] = 'info', ms = tone === 'warn' ? 7000 : 3200) {
    const t = { id: next++, text, tone };
    this.list = [...this.list, t];
    setTimeout(() => this.dismiss(t.id), ms);
  }

  dismiss(id: number) {
    this.list = this.list.filter((t) => t.id !== id);
  }
}

export const toasts = new Toasts();
export const toast = (text: string, tone?: Toast['tone']) => toasts.push(text, tone);
