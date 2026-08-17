import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!;

// Browser singleton — safe to import in Client Components
// The publishable key is Supabase's new key system (equivalent to the anon key).
export const supabase = createClient(supabaseUrl, supabaseKey);
