"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/hooks/useAccessToken";
import { getOrCreateDeviceId } from "@/hooks/useDeviceId";
import { noteAttachmentUrl } from "@/services/notebookService";

export default function NotePhotoThumb({ path }: { path: string | null | undefined }) {
  const [src, setSrc] = useState<string | null>(null);

  useEffect(() => {
    const url = noteAttachmentUrl(path);
    if (!url) return;
    let objectUrl: string | null = null;
    let cancelled = false;
    const headers: Record<string, string> = {};
    const token = getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
    else headers["X-Device-Id"] = getOrCreateDeviceId();

    fetch(url, { headers })
      .then((res) => (res.ok ? res.blob() : null))
      .then((blob) => {
        if (cancelled || !blob) return;
        objectUrl = URL.createObjectURL(blob);
        setSrc(objectUrl);
      })
      .catch(() => {
        /* ignore */
      });

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [path]);

  if (!src) return null;
  // eslint-disable-next-line @next/next/no-img-element
  return <img src={src} alt="" className="notebook-photo-thumb" />;
}
