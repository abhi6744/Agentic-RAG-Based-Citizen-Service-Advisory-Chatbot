import { createContext, PropsWithChildren, useContext, useMemo } from "react";
import { AppColors, colors as fixedColors } from "../constants/colors";

type ThemeContextValue = {
  colors: AppColors;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: PropsWithChildren) {
  const value = useMemo(
    () => ({
      colors: fixedColors,
    }),
    [],
  );

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);

  if (!context) {
    throw new Error("useTheme must be used inside ThemeProvider");
  }

  return context;
}
