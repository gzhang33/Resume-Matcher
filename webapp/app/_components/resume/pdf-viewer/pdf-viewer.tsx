"use client";

import { useEffect, useMemo, useState } from "react";
import { useGlobalStore } from "@/stores/useGlobalStore";

const PDFViewer = () => {
  const { file } = useGlobalStore();

  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);

    return () => {
      URL.revokeObjectURL(objectUrl);
    };
  }, [file]);

  const iframeTitle = useMemo(() => {
    if (!file) return "resume-preview";
    return `resume-preview-${file.name}`;
  }, [file]);

  if (!previewUrl) {
    return (
      <div className="text-center text-slate-500">
        Unable to generate preview for the selected file.
      </div>
    );
  }

  return (
    <div className="w-full flex flex-col gap-4">
      <iframe
        title={iframeTitle}
        src={previewUrl}
        className="w-full h-[800px] border border-slate-700 rounded-md"
      />
      <span className="text-xs text-slate-500">
        Preview powered by the browser&apos;s built-in PDF renderer.
      </span>
    </div>
  );
};

export default PDFViewer;
