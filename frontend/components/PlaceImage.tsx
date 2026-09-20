"use client";

import { useState } from "react";

export default function PlaceImage({
  src,
  alt,
  className,
}: {
  src: string | null | undefined;
  alt: string;
  className?: string;
}) {
  const [failed, setFailed] = useState(false);
  if (!src || failed) {
    return <div className={`${className ?? ""} place-image-fallback`.trim()} aria-hidden />;
  }
  return <img src={src} alt={alt} className={className} onError={() => setFailed(true)} />;
}
