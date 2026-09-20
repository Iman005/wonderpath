import AuthGuard from "@/components/AuthGuard";

export default function TripLayout({ children }: { children: React.ReactNode }) {
  return <AuthGuard>{children}</AuthGuard>;
}
