"use client";

import { useRouter } from "next/navigation";
import fa from "@/i18n/fa";

export default function GuideBackLink() {
  const router = useRouter();

  function goBack() {
    if (typeof window !== "undefined") {
      const ref = document.referrer;
      if (ref) {
        try {
          const url = new URL(ref);
          if (url.origin === window.location.origin && url.pathname !== "/guide") {
            router.back();
            return;
          }
        } catch {
          /* fall through */
        }
      }
    }
    router.push("/app");
  }

  return (
    <button type="button" className="nav-text-btn" onClick={goBack}>
      ← {fa.guide.backHome}
    </button>
  );
}
