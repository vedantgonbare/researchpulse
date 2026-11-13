export function getDefaultRouteForRole(role) {
  return role === "professor" ? "/professor/dashboard" : "/dashboard";
}