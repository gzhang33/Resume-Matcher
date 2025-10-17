"use client";

import { useGlobalStore } from "@/stores/useGlobalStore";

const ProcessingError = () => {
  const { processingError } = useGlobalStore();

  if (!processingError) return null;

  return (
    <div
      role="alert"
      className="flex flex-col gap-3 rounded-md border border-red-300 bg-red-50 p-4 text-red-600"
    >
      <p className="font-medium">
        We could not process the latest request. Please verify that the backend
        service is running and try again.
      </p>
      <pre className="whitespace-pre-wrap break-words text-xs text-red-500">
        {processingError}
      </pre>
    </div>
  );
};

export default ProcessingError;
