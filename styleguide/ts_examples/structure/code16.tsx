{
  /* <REVIEW>данный файл должен находиться по пути "/src/pages/RootPage/RootPage.tsx"</REVIEW> */
}

import { Suspense } from "react";

// <REVIEW>использование готовых ui библиотек запрешено</REVIEW>
import { Flex } from "@chakra-ui/react";

import { Outlet, useLocation } from "react-router-dom";

import { paths } from "@pages/routes";
import {
  CodeLoading,
  CodeLoadingProgress,
  CodeLoadingTitle,
} from "@shared/ui/loading";
import { Footer } from "@widgets/Footer";
import { Header } from "@widgets/Header";

const Root = () => {
  const location = useLocation();

  return (
    <Flex
      direction="column"
      h={location.pathname === paths.typingCodePage ? "100vh" : "auto"}
      minH="100vh"
    >
      <Header />

      <Flex as="main" flex="1" overflow="hidden" py="1px">
        <Suspense
          fallback={
            <CodeLoading>
              <CodeLoadingTitle />
              <CodeLoadingProgress />
            </CodeLoading>
          }
        >
          <Outlet />
        </Suspense>
      </Flex>

      <Footer />
    </Flex>
  );
};

export default Root;
