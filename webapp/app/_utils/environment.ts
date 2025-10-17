/**
 * Returns a boolean indicating whether the code is running in a development environment.
 * @returns {boolean} - True if the code is running in a development environment, false otherwise.
 */
export function isRunningInDevEnvironment(): boolean {
  return process.env.NODE_ENV === "development";
}

/**
 * Returns the protocol and host of the current request.
 * This is a client-side utility.
 * @returns A string representing the protocol and host of the current request.
 */
export function getProtocolAndHost(): string {
  if (typeof window === "undefined") {
    // This function is intended for client-side use.
    // On the server, we can't know the host without passing it from a server component.
    return "http://localhost:3000";
  }
  return window.location.origin;
}