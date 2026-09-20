"use client";

import { useEffect, useSyncExternalStore, type HTMLAttributes, type ReactNode } from "react";
import { createPortal } from "react-dom";

let scrollLocks = 0;
let previousOverflow = "";

function lockBodyScroll() {
  if (scrollLocks === 0) {
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
  }
  scrollLocks += 1;
  return () => {
    scrollLocks = Math.max(0, scrollLocks - 1);
    if (scrollLocks === 0) {
      document.body.style.overflow = previousOverflow;
    }
  };
}

const subscribe = () => () => {};

export default function AppOverlay({
  children,
  className,
  ...rest
}: HTMLAttributes<HTMLDivElement> & { children: ReactNode }) {
  const mounted = useSyncExternalStore(subscribe, () => true, () => false);
  useEffect(() => lockBodyScroll(), []);

  if (!mounted) return null;

  return createPortal(
    <div className={["app-overlay", className].filter(Boolean).join(" ")} {...rest}>
      {children}
    </div>,
    document.body,
  );
}
