import os
import requests
from openai import OpenAI

from prompt import PromptGenerator


client = OpenAI(api_key=os.environ["VSE_GPT_API_KEY"], base_url="https://api.vsegpt.ru/v1")
# client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

def get_response(
    system_prompt: str, user_prompt: str, context: dict[str, list[str]]
) -> str:
    messages = [{"role": "system", "content": system_prompt}]
    for prompt, model_response in zip(context["user"], context["assistant"]):
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "assistant", "content": model_response})

    messages.append({"role": "user", "content": user_prompt})
    
    response = client.chat.completions.create(
        model="qwen/qwen-2.5-coder-32b-instruct",
        # model="google/gemma-2-27b-it",
        # model="deepseek-instruct",
        messages=messages,
        stream=False,
        temperature=0.15
    )

    return response.choices[0].message.content


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
    # user_prompt = PromptGenerator("tsx").generate_user_prompt(code)
    user_prompt = code

    context = PromptGenerator("tsx").generate_context(code)
    
    response = get_response(system_prompt, user_prompt, context)
    print(response)


if __name__ == "__main__":
    main()
    