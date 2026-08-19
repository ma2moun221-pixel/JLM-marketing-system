import { NextResponse, type NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login"];

function hasSessionCookie(request: NextRequest): boolean {
  return Boolean(
    request.cookies.get("authjs.session-token") ??
      request.cookies.get("__Secure-authjs.session-token"),
  );
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isPublic = PUBLIC_PATHS.some((p) => pathname.startsWith(p));
  const isAuthApi = pathname.startsWith("/api/auth");

  let response: NextResponse;

  if (!isPublic && !isAuthApi && !hasSessionCookie(request)) {
    const loginUrl = new URL("/login", request.url);
    response = NextResponse.redirect(loginUrl);
  } else {
    response = NextResponse.next();
  }

  // Never index — this is a private internal platform.
  response.headers.set("X-Robots-Tag", "noindex, nofollow");
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
