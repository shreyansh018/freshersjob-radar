import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

export const registerSchema = loginSchema;

export const preferencesSchema = z.object({
  roles: z.array(z.string()),
  locations: z.array(z.string()),
  skills: z.array(z.string()),
  experience: z.string().nullable(),
  remote_preference: z.string().nullable(),
});

export type LoginValues = z.infer<typeof loginSchema>;
export type PreferencesValues = z.infer<typeof preferencesSchema>;
