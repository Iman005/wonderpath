from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def parse_env(path: Path) -> dict[str, str]:
    vals: dict[str, str] = {}
    if not path.exists():
        return vals
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        vals[key.strip()] = value.strip().strip('"').strip("'")
    return vals


def main() -> None:
    backend = parse_env(ROOT / "backend" / ".env")
    frontend = parse_env(ROOT / "frontend" / ".env")
    frontend.update(parse_env(ROOT / "frontend" / ".env.local"))
    google = frontend.get("NEXT_PUBLIC_GOOGLE_CLIENT_ID") or backend.get("GOOGLE_CLIENT_ID") or ""
    neshan = frontend.get("NEXT_PUBLIC_NESHAN_API_KEY") or backend.get("NESHAN_API_KEY") or ""
    pairs = [
        ("NEXT_PUBLIC_API_BASE_URL", "https://backend-production-6cd6.up.railway.app"),
    ]
    if google:
        pairs.append(("NEXT_PUBLIC_GOOGLE_CLIENT_ID", google))
    if neshan:
        pairs.append(("NEXT_PUBLIC_NESHAN_API_KEY", neshan))
    cwd = ROOT / "frontend"
    for key, value in pairs:
        result = subprocess.run(
            ["netlify.cmd", "env:set", key, value],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            raise SystemExit(result.stderr or result.stdout)
        print("set", key)


if __name__ == "__main__":
    main()
