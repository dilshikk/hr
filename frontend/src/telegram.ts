// Минимальные типы Telegram WebApp, которые мы используем.
type BackButton = {
  show(): void;
  hide(): void;
  onClick(cb: () => void): void;
  offClick(cb: () => void): void;
};

type WebApp = {
  initData: string;
  ready(): void;
  expand(): void;
  BackButton: BackButton;
  HapticFeedback?: { notificationOccurred(t: "success" | "error"): void };
};

declare global {
  interface Window {
    Telegram?: { WebApp: WebApp };
  }
}

export const tg: WebApp | undefined = window.Telegram?.WebApp;

export function haptic(type: "success" | "error") {
  tg?.HapticFeedback?.notificationOccurred(type);
}
