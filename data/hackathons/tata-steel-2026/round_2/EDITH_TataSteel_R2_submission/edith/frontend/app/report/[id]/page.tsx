import { ReportView } from "@/components/cockpit/report-view";

interface ReportPageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ print?: string }>;
}

export default async function ReportPage({ params, searchParams }: ReportPageProps) {
  const { id } = await params;
  const { print } = await searchParams;
  return <ReportView reportId={id} printMode={print === "1"} />;
}
