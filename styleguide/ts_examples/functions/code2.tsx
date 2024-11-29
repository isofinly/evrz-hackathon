import {
  CssBaseline,
  Experimental_CssVarsProvider as CssVarsProvider,
  StyledEngineProvider,
  experimental_extendTheme as extendTheme,
} from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import * as React from "react";

export const withGlobalStyles =
  (Component: React.ComponentType): React.ComponentType =>
  () => {
    return (
      <CssVarsProvider theme={theme}>
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <StyledEngineProvider injectFirst>
            <CssBaseline />
            <Component />
          </StyledEngineProvider>
        </LocalizationProvider>
      </CssVarsProvider>
    );
  };

const theme = extendTheme({
  shape: {
    borderRadius: 8,
  },
  spacing: (tab: number) => `${tab}rem`,
  colorSchemes: {
    dark: {
      palette: {
        common: {
          background: "#121212",
        },
      },
    },
  },
  components: {
    MuiButton: {
      defaultProps: {
        variant: "contained",
        disableElevation: true,
      },
    },
    MuiPaper: {
      defaultProps: {
        variant: "outlined",
        elevation: 0,
        sx: {
          borderWidth: 2,
        },
      },
    },
    MuiSkeleton: {
      styleOverrides: {
        root: {
          transform: "scale(1)",
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paperFullScreen: {
          height: "100dvh",
        },
      },
    },
  },
});