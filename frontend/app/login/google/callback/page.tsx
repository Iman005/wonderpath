"use client";

import { useEffect } from "react";
import fa from "@/i18n/fa";
import {
  GOOGLE_AUTH_MESSAGE,
  publishGoogleAuthResult,
  readGoogleHash,
} from "@/modules/auth/googlePopup";

export default function GoogleCallbackPage() {
  useEffect(() => {
    const { idToken, error } = readGoogleHash(window.location.hash);
    publishGoogleAuthResult({
      source: GOOGLE_AUTH_MESSAGE,
      id_token: idToken,
      error,
    });

    window.setTimeout(() => {
      window.close();
      // Full-tab Google redirect (no popup): return to login with stored token.
      if (!window.closed) {
        window.location.replace("/login");
      }
    }, 80);
  }, []);

  return <p className="muted container">{fa.common.loading}</p>;
}
