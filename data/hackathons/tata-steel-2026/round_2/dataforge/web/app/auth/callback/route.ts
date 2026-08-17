import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@supabase/supabase-js";

/**
 * Supabase OAuth callback handler.
 *
 * After a Google (or other OAuth) flow, Supabase redirects to:
 *   /auth/callback?code=<code>&next=<url>
 *
 * We exchange the code for a session using the server-side client,
 * then redirect the user to `next` (or "/" as fallback).
 *
 * Note: `@supabase/ssr` provides a more integrated cookie-based session
 * management approach for Next.js App Router. This lightweight version
 * uses the standard JS client to exchange the code, which works for the
 * hackathon demo scope (no SSR-gated routes). For production, upgrade to
 * @supabase/ssr.
 */
export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const next = searchParams.get("next") ?? "/";

  if (code) {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
    const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!;
    const serverClient = createClient(supabaseUrl, supabaseKey);

    const { error } = await serverClient.auth.exchangeCodeForSession(code);
    if (!error) {
      // Redirect to destination — session cookie set by Supabase client
      return NextResponse.redirect(`${origin}${next}`);
    }
  }

  // On error, redirect to login with an error hint
  return NextResponse.redirect(`${origin}/login?error=oauth_failed`);
}
