import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { User } from "@/types";

/** The API keeps the session in an HttpOnly cookie; this query just reads it. */
export function useAuth() {
  const queryClient = useQueryClient();
  const me = useQuery<User | null>({
    queryKey: ["me"],
    queryFn: async () => {
      try {
        return await api.me();
      } catch {
        return null; // 401 = not signed in
      }
    },
    retry: false,
    staleTime: 5 * 60_000,
  });

  return {
    user: me.data ?? null,
    isLoading: me.isLoading,
    setUser: (user: User | null) => queryClient.setQueryData<User | null>(["me"], user),
    signOut: async () => {
      try {
        await api.logout();
      } catch {
        // clear local state even if the request fails
      }
      queryClient.setQueryData<User | null>(["me"], null);
    },
  };
}

export function displayName(user: User | null | undefined): string | null {
  if (!user) return null;
  return user.email.split("@")[0];
}
