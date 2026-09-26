// Short messages that say what just happened to what he did, then leave on their own.

export interface Toast {
  id: number;
  text: string;
  tone: 'ok' | 'info' | 'warn';
  /** Toasts with the same key replace each other, so a run of saves is one message (P31). */
  key?: string;
}

let next = 1;

class Toasts {
  list = $state<Toast[]>([]);
  #timers = new Map<number, ReturnType<typeof setTimeout>>();

  push(text: string, tone: Toast['tone'] = 'info', key?: string, ms = tone === 'warn' ? 7000 : 3200) {
    const same = key ? this.list.find((t) => t.key === key) : undefined;
    if (same) {
      clearTimeout(this.#timers.get(same.id));
      this.list = this.list.map((t) => (t.id === same.id ? { ...t, text, tone } : t));
      this.#timers.set(same.id, setTimeout(() => this.dismiss(same.id), ms));
      return;
    }
    const t = { id: next++, text, tone, key };
    this.list = [...this.list, t].slice(-3);
    this.#timers.set(t.id, setTimeout(() => this.dismiss(t.id), ms));
  }

  dismiss(id: number) {
    this.list = this.list.filter((t) => t.id !== id);
    this.#timers.delete(id);
  }
}

export const toasts = new Toasts();
export const toast = (text: string, tone?: Toast['tone'], key?: string) => toasts.push(text, tone, key);
