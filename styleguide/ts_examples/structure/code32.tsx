import "./global.css";
import "@fontsource/nunito/400.css";
import "@fontsource/nunito/500.css";
import "@fontsource/nunito/700.css";
import { H } from "highlight.run";
import React from "react";
import ReactDOM from "react-dom/client";
import { App, appStarted } from "@app";

H.init(window.ENV.CLIENT_HIGHLIGHT_PROJECT_ID, {
  manualStart: true,
  environment: window.ENV.NODE_ENV,
  version: window.ENV.CLIENT_VERSION,
  tracingOrigins: [window.ENV.CLIENT_API_URL.replace("https://", "")],
  networkRecording: {
    enabled: true,
    recordHeadersAndBody: true,
  },
});
if (window.ENV.NODE_ENV === "production") {
  H.start();
}
let shouldRender = true;
if (window.navigator.userAgent.includes("Windows")) {
  if (localStorage.getItem("reloaded") === "1") {
    localStorage.removeItem("reloaded");
  } else {
    localStorage.setItem("reloaded", "1");
    window.location.reload();
    shouldRender = false;
  }
}
if (shouldRender) {
  const container = document.querySelector("#root") as HTMLElement;
  const root = ReactDOM.createRoot(container);

  appStarted();

  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}
