const LAST_EMAIL_KEY = "wanderpath_last_email";
const LAST_PASSWORD_KEY = "wanderpath_last_password";

type PasswordCredLike = {
  id: string;
  password?: string;
};

function passwordCredentialCtor():
  | (new (data: { id: string; password: string; name?: string }) => PasswordCredLike)
  | null {
  if (typeof window === "undefined") return null;
  const ctor = (window as unknown as { PasswordCredential?: unknown }).PasswordCredential;
  return typeof ctor === "function"
    ? (ctor as new (data: { id: string; password: string; name?: string }) => PasswordCredLike)
    : null;
}

function canUsePasswordManager() {
  return Boolean(passwordCredentialCtor() && navigator.credentials?.store);
}

export function getRememberedEmail(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem(LAST_EMAIL_KEY) || "";
}

export function getRememberedPassword(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem(LAST_PASSWORD_KEY) || "";
}

export function rememberEmail(email: string) {
  const cleaned = email.trim();
  if (cleaned) localStorage.setItem(LAST_EMAIL_KEY, cleaned);
}

export function forgetRememberedEmail() {
  localStorage.removeItem(LAST_EMAIL_KEY);
  localStorage.removeItem(LAST_PASSWORD_KEY);
}

/** Persist email + password for the next visit (local device). */
export async function storePasswordCredentials(email: string, password: string, name?: string) {
  const cleanedEmail = email.trim();
  if (!cleanedEmail || !password) return;

  rememberEmail(cleanedEmail);
  localStorage.setItem(LAST_PASSWORD_KEY, password);

  const Ctor = passwordCredentialCtor();
  if (!Ctor || !navigator.credentials?.store) return;
  try {
    const credential = new Ctor({
      id: cleanedEmail,
      password,
      name: (name || "").trim() || cleanedEmail,
    });
    await navigator.credentials.store(credential as Credential);
  } catch {
    // localStorage already holds the values for next visit.
  }
}

export async function readPasswordCredentials(): Promise<{ email: string; password: string } | null> {
  const localEmail = getRememberedEmail();
  const localPassword = getRememberedPassword();
  if (localEmail && localPassword) {
    return { email: localEmail, password: localPassword };
  }

  if (!canUsePasswordManager() || !navigator.credentials?.get) {
    return localEmail ? { email: localEmail, password: "" } : null;
  }

  try {
    const credential = await navigator.credentials.get({
      password: true,
      mediation: "optional",
    } as CredentialRequestOptions);
    if (!credential || !("password" in credential)) {
      return localEmail ? { email: localEmail, password: localPassword } : null;
    }
    const password = String((credential as PasswordCredLike).password || "");
    const email = credential.id || localEmail;
    if (!email) return null;
    if (password) {
      localStorage.setItem(LAST_PASSWORD_KEY, password);
      rememberEmail(email);
    }
    return { email, password: password || localPassword };
  } catch {
    return localEmail ? { email: localEmail, password: localPassword } : null;
  }
}
