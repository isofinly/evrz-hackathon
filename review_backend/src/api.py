import os
import requests

from prompt import PromptGenerator


MODEL_API_KEY = os.getenv("MODEL_API_KEY")
URL = "http://84.201.152.196:8020/v1/completions"


def get_response(
    system_prompt: str, user_prompt: str, context: dict[str, list[str]]
) -> str:
    headers = {"Authorization": MODEL_API_KEY, "Content-Type": "application/json"}

    messages = [{"role": "system", "content": system_prompt}]
    for prompt, model_response in zip(context["user"], context["assistant"]):
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "assistant", "content": model_response})

    messages.append({"role": "user", "content": user_prompt})

    data = {
        "model": "mistral-nemo-instruct-2407",
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.2,
    }

    response = requests.post(URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    
    raise RuntimeError(response.json()["error"]["message"])


def main():
    code = """
1 import { Suspense } from "react";
2
3 import { Flex } from "@chakra-ui/react";
4
5 import { Outlet, useLocation } from "react-router-dom";
6
7 import { paths } from "@pages/routes";
8
9 import {
10   CodeLoading,
11   CodeLoadingProgress,
12   CodeLoadingTitle,
13 } from "@shared/ui/loading";
14
15 import { Footer } from "@widgets/Footer";
16 import { Header } from "@widgets/Header";
17
18 const Root = () => {
19   const location = useLocation();
20
21   return (
22     <Flex
23     direction="column"
24     h={location.pathname === paths.typingCodePage ? "100vh" : "auto"}
25     minH="100vh"
26    >
27      <Header />
28
29      <Flex as="main" flex="1" overflow="hidden" py="1px">
30        <Suspense
31          fallback={
32            <CodeLoading>
33              <CodeLoadingTitle />
34              <CodeLoadingProgress />
35            </CodeLoading>
36          }
37        >
38          <Outlet />
39        </Suspense>
40      </Flex>
41
42      <Footer />
43    </Flex>
44  );
45 };
46
47 export default Root;
"""
    
    system_prompt = PromptGenerator("tsx").generate_system_prompt()
    user_prompt = PromptGenerator("tsx").generate_user_prompt(code)
    
    context = PromptGenerator("tsx").generate_context(code)
    
    response = get_response(system_prompt, user_prompt, context)
    print(response)


if __name__ == "__main__":
    main()
    