"use client";

import { useEffect, useState } from "react";
import SavedKeys from "@/app/_components/third-party-services/saved-keys";
import { getErrorMessage } from "@/utils/errors";
import { GetServiceKeysResponse, ServiceKeys } from "@/types/service-keys";
import {
  getProtocolAndHost,
  isRunningInDevEnvironment,
} from "@/utils/environment";

type ServiceKeyState =
  | { status: "loading" }
  | { status: "ready"; keys: ServiceKeys }
  | { status: "empty" }
  | { status: "error"; error: string };

async function getServiceKeys(): Promise<GetServiceKeysResponse> {
  const isDevEnvironment = isRunningInDevEnvironment();
  let url = "/api/service-keys";

  if (isDevEnvironment) {
    const protocolHost = getProtocolAndHost();
    url = `${protocolHost}${url}`;
  }

  try {
    const response = await fetch(url, { cache: "no-store" });

    if (!response.ok) {
      const details = await response.text();
      return {
        error: `Failed to load service keys. Status: ${response.status}. Details: ${details}`,
      };
    }

    const data = (await response.json()) as GetServiceKeysResponse;

    return data;
  } catch (error) {
    console.error(error);
    return {
      error: getErrorMessage(error),
    };
  }
}

const ThirdPartyServicesKeys = () => {
  const [state, setState] = useState<ServiceKeyState>({ status: "loading" });

  useEffect(() => {
    let isMounted = true;

    async function loadServiceKeys() {
      const data = await getServiceKeys();

      if (!isMounted) {
        return;
      }

      if (
        data.error ||
        !data?.config_keys ||
        Object.keys(data.config_keys).length === 0
      ) {
        setState({ status: "empty" });
        return;
      }

      setState({ status: "ready", keys: data.config_keys });
    }

    loadServiceKeys();

    return () => {
      isMounted = false;
    };
  }, []);

  if (state.status !== "ready") {
    return null;
  }

  return (
    <section className="flex flex-col gap-4 w-full px-32 py-10">
      <h2 className="text-3xl font-normal leading-normal">Service Keys</h2>
      <div className="flex flex-col gap-4 text-black p-4 bg-transparent border-2 border-[#2C203E]">
        <SavedKeys keys={state.keys} />
      </div>
    </section>
  );
};

export default ThirdPartyServicesKeys;
