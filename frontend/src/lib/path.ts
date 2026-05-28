const rawBasePath = process.env.NEXT_PUBLIC_BASE_PATH || "";

export const BASE_PATH = rawBasePath === "/" ? "" : rawBasePath.replace(/\/+$/, "");

export function withBasePath(path: string = "/") {
  const normalizedInput = path.startsWith("/") ? path : `/${path}`;
  const queryIndex = normalizedInput.search(/[?#]/);
  const pathname = queryIndex >= 0 ? normalizedInput.slice(0, queryIndex) : normalizedInput;
  const suffix = queryIndex >= 0 ? normalizedInput.slice(queryIndex) : "";
  const trailingPath = pathname === "/" ? "/" : pathname.endsWith("/") ? pathname : `${pathname}/`;

  if (!BASE_PATH) {
    return `${trailingPath}${suffix}`;
  }

  return trailingPath === "/" ? `${BASE_PATH}/` : `${BASE_PATH}${trailingPath}${suffix}`;
}
