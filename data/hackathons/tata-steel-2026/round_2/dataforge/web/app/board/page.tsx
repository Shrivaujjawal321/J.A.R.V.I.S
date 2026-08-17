import { redirect } from "next/navigation";

// /board was the v1 dataset board — permanently redirected to /datasets in v2.
export default function BoardPage() {
  redirect("/datasets");
}
