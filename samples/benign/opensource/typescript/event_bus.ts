// Source: TypeScript Benign Sample
// Generated: 2026-04-02 11:48:04.520539

/**
 * 事件总线 - 良性
 */
type EventHandler = (data: any) => void;

class EventBus {
  private handlers: Map<string, Set<EventHandler>> = new Map();
  
  on(event: string, handler: EventHandler): void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler);
  }
  
  emit(event: string, data: any): void {
    const handlers = this.handlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }
  
  off(event: string, handler: EventHandler): void {
    const handlers = this.handlers.get(event);
    if (handlers) {
      handlers.delete(handler);
    }
  }
}

export default new EventBus();
